"""
Order Service Client
"""
from typing import Optional, List, Dict
from .base_client import BaseClient

class OrderClient(BaseClient):
    """
    Client for Order Service API
    """
    
    def __init__(self, base_url: str = "http://order-service:8000"):
        super().__init__(base_url)
    
    async def get_user_orders(
        self,
        user_id: int,
        limit: int = 50
    ) -> List[Dict]:
        """
        Get user's order history
        
        Args:
            user_id: User ID
            limit: Maximum number of orders
            
        Returns:
            List of orders
        """
        params = {"user_id": user_id, "limit": limit}
        response = await self.get("/api/orders/", params=params)
        
        if response and "results" in response:
            return response["results"]
        
        return []
    
    async def get_order(self, order_id: int) -> Optional[Dict]:
        """
        Get order by ID
        
        Args:
            order_id: Order ID
            
        Returns:
            Order data or None
        """
        return await self.get(f"/api/orders/{order_id}/")
    
    async def get_user_purchase_history(
        self,
        user_id: int
    ) -> List[int]:
        """
        Get list of product IDs user has purchased
        
        Args:
            user_id: User ID
            
        Returns:
            List of product IDs
        """
        orders = await self.get_user_orders(user_id)
        
        product_ids = []
        for order in orders:
            if "items" in order:
                for item in order["items"]:
                    if "product_id" in item:
                        product_ids.append(item["product_id"])
        
        return list(set(product_ids))  # Remove duplicates
    
    async def get_user_interaction_sequence(
        self,
        user_id: int,
        max_length: int = 20
    ) -> List[int]:
        """
        Get user's product interaction sequence
        (ordered by purchase date)
        
        Args:
            user_id: User ID
            max_length: Maximum sequence length
            
        Returns:
            List of product IDs in chronological order
        """
        orders = await self.get_user_orders(user_id, limit=max_length)
        
        # Sort by created date
        orders.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        
        sequence = []
        for order in orders:
            if "items" in order:
                for item in order["items"]:
                    if "product_id" in item:
                        sequence.append(item["product_id"])
        
        return sequence[:max_length]
