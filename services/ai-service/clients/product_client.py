"""
Product Service Client
"""
from typing import Optional, List, Dict
from .base_client import BaseClient

class ProductClient(BaseClient):
    """
    Client for Product Service API
    """
    
    def __init__(self, base_url: str = "http://product-service:8000"):
        super().__init__(base_url)
    
    async def get_product(self, product_id: int) -> Optional[Dict]:
        """
        Get product by ID
        
        Args:
            product_id: Product ID
            
        Returns:
            Product data or None
        """
        return await self.get(f"/api/products/{product_id}/")
    
    async def get_products(self, product_ids: List[int]) -> List[Dict]:
        """
        Get multiple products by IDs
        
        Args:
            product_ids: List of product IDs
            
        Returns:
            List of product data
        """
        products = []
        
        for product_id in product_ids:
            product = await self.get_product(product_id)
            if product:
                products.append(product)
        
        return products
    
    async def get_all_products(
        self,
        category: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict]:
        """
        Get all products with optional filtering
        
        Args:
            category: Filter by category
            limit: Maximum number of products
            
        Returns:
            List of products
        """
        params = {"limit": limit}
        if category:
            params["category"] = category
        
        response = await self.get("/api/products/", params=params)
        
        if response and "results" in response:
            return response["results"]
        
        return []
    
    async def check_stock(self, product_id: int) -> Optional[int]:
        """
        Check product stock
        
        Args:
            product_id: Product ID
            
        Returns:
            Stock quantity or None
        """
        response = await self.get(f"/api/products/{product_id}/check-stock/")
        
        if response and "stock" in response:
            return response["stock"]
        
        return None
    
    async def get_product_details_batch(
        self,
        product_ids: List[int]
    ) -> Dict[int, Dict]:
        """
        Get product details for multiple products
        Returns dict mapping product_id to product data
        
        Args:
            product_ids: List of product IDs
            
        Returns:
            Dictionary mapping product_id to product data
        """
        products = await self.get_products(product_ids)
        
        return {
            product["id"]: product
            for product in products
            if "id" in product
        }
