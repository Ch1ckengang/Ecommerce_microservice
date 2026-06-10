"""
Service Manager - Manages all microservice clients
"""
import os
from typing import Optional, List, Dict
from clients.product_client import ProductClient
from clients.order_client import OrderClient
from clients.user_client import UserClient

class ServiceManager:
    """
    Manages communication with other microservices
    """
    
    def __init__(self):
        """Initialize service manager with all clients"""
        # Get service URLs from environment variables
        product_url = os.getenv("PRODUCT_SERVICE_URL", "http://localhost:8001")
        order_url = os.getenv("ORDER_SERVICE_URL", "http://localhost:8002")
        user_url = os.getenv("USER_SERVICE_URL", "http://localhost:8003")
        
        # Initialize clients
        self.product_client = ProductClient(product_url)
        self.order_client = OrderClient(order_url)
        self.user_client = UserClient(user_url)
        
        print(f"✅ Service Manager initialized")
        print(f"   Product Service: {product_url}")
        print(f"   Order Service: {order_url}")
        print(f"   User Service: {user_url}")
    
    async def close(self):
        """Close all client connections"""
        await self.product_client.close()
        await self.order_client.close()
        await self.user_client.close()
        print("✅ Service Manager closed")
    
    async def get_user_context(self, user_id: int) -> Dict:
        """
        Get comprehensive user context for recommendations
        
        Args:
            user_id: User ID
            
        Returns:
            Dictionary with user context
        """
        # Get user info
        user = await self.user_client.get_user(user_id)
        
        # Get user preferences
        preferences = await self.user_client.get_user_preferences(user_id)
        
        # Get purchase history
        purchase_history = await self.order_client.get_user_purchase_history(user_id)
        
        # Get interaction sequence
        interaction_sequence = await self.order_client.get_user_interaction_sequence(user_id)
        
        return {
            "user_id": user_id,
            "user": user,
            "preferences": preferences,
            "purchase_history": purchase_history,
            "interaction_sequence": interaction_sequence
        }
    
    async def enrich_recommendations(
        self,
        recommendations: List[tuple]
    ) -> List[Dict]:
        """
        Enrich recommendations with product details
        
        Args:
            recommendations: List of (product_id, scores) tuples
            
        Returns:
            List of enriched recommendations
        """
        # Extract product IDs
        product_ids = [pid for pid, _ in recommendations]
        
        # Get product details
        products = await self.product_client.get_product_details_batch(product_ids)
        
        # Enrich recommendations
        enriched = []
        for product_id, scores in recommendations:
            product_data = products.get(product_id, {})
            
            enriched.append({
                "product_id": product_id,
                "score": scores.get("final_score", 0.0),
                "breakdown": {
                    "lstm": scores.get("lstm", 0.0),
                    "graph": scores.get("graph", 0.0),
                    "rag": scores.get("rag", 0.0)
                },
                "product": {
                    "name": product_data.get("name", f"Product {product_id}"),
                    "category": product_data.get("category", "Unknown"),
                    "price": product_data.get("price", 0),
                    "image": product_data.get("image", ""),
                    "stock": product_data.get("stock", 0)
                }
            })
        
        return enriched
    
    async def get_smart_recommendations(
        self,
        user_id: int,
        k: int = 10
    ) -> Dict:
        """
        Get smart recommendations using user context
        
        Args:
            user_id: User ID
            k: Number of recommendations
            
        Returns:
            Dictionary with recommendations and context
        """
        # Get user context
        context = await self.get_user_context(user_id)
        
        return {
            "user_id": user_id,
            "context": context,
            "recommendations_ready": True,
            "interaction_sequence": context["interaction_sequence"],
            "purchase_history": context["purchase_history"]
        }
    
    async def check_products_availability(
        self,
        product_ids: List[int]
    ) -> Dict[int, bool]:
        """
        Check if products are available (in stock)
        
        Args:
            product_ids: List of product IDs
            
        Returns:
            Dictionary mapping product_id to availability
        """
        availability = {}
        
        for product_id in product_ids:
            stock = await self.product_client.check_stock(product_id)
            availability[product_id] = stock is not None and stock > 0
        
        return availability
    
    async def filter_available_recommendations(
        self,
        recommendations: List[tuple]
    ) -> List[tuple]:
        """
        Filter recommendations to only include available products
        
        Args:
            recommendations: List of (product_id, scores) tuples
            
        Returns:
            Filtered list of recommendations
        """
        product_ids = [pid for pid, _ in recommendations]
        availability = await self.check_products_availability(product_ids)
        
        return [
            (pid, scores)
            for pid, scores in recommendations
            if availability.get(pid, False)
        ]
