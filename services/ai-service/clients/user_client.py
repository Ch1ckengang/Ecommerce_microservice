"""
User Service Client
"""
from typing import Optional, Dict
from .base_client import BaseClient

class UserClient(BaseClient):
    """
    Client for User Service API
    """
    
    def __init__(self, base_url: str = "http://user-service:8000"):
        super().__init__(base_url)
    
    async def get_user(self, user_id: int) -> Optional[Dict]:
        """
        Get user by ID
        
        Args:
            user_id: User ID
            
        Returns:
            User data or None
        """
        return await self.get(f"/api/users/{user_id}/")
    
    async def get_user_profile(self, user_id: int) -> Optional[Dict]:
        """
        Get user profile with preferences
        
        Args:
            user_id: User ID
            
        Returns:
            User profile or None
        """
        return await self.get(f"/api/users/{user_id}/profile/")
    
    async def get_user_preferences(self, user_id: int) -> Dict:
        """
        Get user preferences for recommendations
        
        Args:
            user_id: User ID
            
        Returns:
            Dictionary with user preferences
        """
        profile = await self.get_user_profile(user_id)
        
        if not profile:
            return {}
        
        return {
            "favorite_categories": profile.get("favorite_categories", []),
            "price_range": profile.get("price_range", {}),
            "brands": profile.get("favorite_brands", [])
        }
