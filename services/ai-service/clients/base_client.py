"""
Base HTTP Client for microservices communication
"""
import httpx
from typing import Optional, Dict, Any
import asyncio
from functools import wraps

class BaseClient:
    """
    Base client for HTTP communication with retry logic
    """
    
    def __init__(
        self,
        base_url: str,
        timeout: float = 10.0,
        max_retries: int = 3
    ):
        """
        Initialize base client
        
        Args:
            base_url: Base URL of the service
            timeout: Request timeout in seconds
            max_retries: Maximum number of retries
        """
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.max_retries = max_retries
        self.client = httpx.AsyncClient(timeout=timeout)
    
    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()
    
    async def _request_with_retry(
        self,
        method: str,
        endpoint: str,
        **kwargs
    ) -> Optional[Dict[Any, Any]]:
        """
        Make HTTP request with retry logic
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint
            **kwargs: Additional arguments for httpx
            
        Returns:
            Response JSON or None if failed
        """
        url = f"{self.base_url}{endpoint}"
        
        for attempt in range(self.max_retries):
            try:
                response = await self.client.request(method, url, **kwargs)
                response.raise_for_status()
                return response.json()
            
            except httpx.HTTPStatusError as e:
                if e.response.status_code >= 500 and attempt < self.max_retries - 1:
                    # Retry on server errors
                    await asyncio.sleep(2 ** attempt)  # Exponential backoff
                    continue
                else:
                    print(f"HTTP error {e.response.status_code}: {url}")
                    return None
            
            except httpx.RequestError as e:
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(2 ** attempt)
                    continue
                else:
                    print(f"Request error: {url} - {e}")
                    return None
            
            except Exception as e:
                print(f"Unexpected error: {url} - {e}")
                return None
        
        return None
    
    async def get(self, endpoint: str, params: Optional[Dict] = None) -> Optional[Dict]:
        """GET request"""
        return await self._request_with_retry("GET", endpoint, params=params)
    
    async def post(self, endpoint: str, json: Optional[Dict] = None) -> Optional[Dict]:
        """POST request"""
        return await self._request_with_retry("POST", endpoint, json=json)
    
    async def put(self, endpoint: str, json: Optional[Dict] = None) -> Optional[Dict]:
        """PUT request"""
        return await self._request_with_retry("PUT", endpoint, json=json)
    
    async def delete(self, endpoint: str) -> Optional[Dict]:
        """DELETE request"""
        return await self._request_with_retry("DELETE", endpoint)
