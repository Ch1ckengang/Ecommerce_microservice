"""
API Client for communicating with backend microservices
"""
import requests
from django.conf import settings
from typing import Optional, Dict, Any
from urllib.parse import parse_qs, urlparse


class APIClient:
    """Base API client for backend services"""
    timeout = (3.05, 10)
    
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.session = requests.Session()
    
    def _get_headers(self, token: Optional[str] = None) -> Dict[str, str]:
        """Get request headers"""
        headers = {
            'Content-Type': 'application/json',
        }
        if token:
            headers['Authorization'] = f'Bearer {token}'
        return headers
    
    def get(self, endpoint: str, token: Optional[str] = None, params: Optional[Dict] = None) -> Dict[str, Any]:
        """Make GET request"""
        url = f"{self.base_url}{endpoint}"
        headers = self._get_headers(token)
        response = self.session.get(url, headers=headers, params=params, timeout=self.timeout)
        response.raise_for_status()
        return response.json()
    
    def post(self, endpoint: str, data: Dict[str, Any], token: Optional[str] = None) -> Dict[str, Any]:
        """Make POST request"""
        url = f"{self.base_url}{endpoint}"
        headers = self._get_headers(token)
        response = self.session.post(url, json=data, headers=headers, timeout=self.timeout)
        response.raise_for_status()
        return response.json()
    
    def put(self, endpoint: str, data: Dict[str, Any], token: Optional[str] = None) -> Dict[str, Any]:
        """Make PUT request"""
        url = f"{self.base_url}{endpoint}"
        headers = self._get_headers(token)
        response = self.session.put(url, json=data, headers=headers, timeout=self.timeout)
        response.raise_for_status()
        return response.json()
    
    def delete(self, endpoint: str, token: Optional[str] = None) -> Dict[str, Any]:
        """Make DELETE request"""
        url = f"{self.base_url}{endpoint}"
        headers = self._get_headers(token)
        response = self.session.delete(url, headers=headers, timeout=self.timeout)
        response.raise_for_status()
        return response.json()


# Service clients
class UserServiceClient(APIClient):
    """Client for User Service"""
    
    def __init__(self):
        super().__init__(settings.USER_SERVICE_URL)
    
    def login(self, username: str, password: str) -> Dict[str, Any]:
        """Login user and fetch profile details"""
        token_resp = self.post('/users/token/', {'username': username, 'password': password})
        if token_resp.get('success'):
            token_data = token_resp.get('data', {})
            access_token = token_data.get('access')
            
            # Fetch profile details using the access token
            profile_resp = self.get('/users/me/', token=access_token)
            if profile_resp.get('success'):
                user_data = profile_resp.get('data', {})
                return {
                    'access': access_token,
                    'refresh': token_data.get('refresh'),
                    'user': user_data
                }
        return {}
    
    def register(self, username: str, email: str, password: str) -> Dict[str, Any]:
        """Register new user"""
        return self.post('/users/register/', {
            'username': username,
            'email': email,
            'password': password,
            'password_confirm': password
        })
    
    def get_profile(self, token: str) -> Dict[str, Any]:
        """Get user profile"""
        response = self.get('/users/me/', token=token)
        if response.get('success'):
            return response.get('data', {})
        return {}


class ProductServiceClient(APIClient):
    """Client for Product Service"""
    
    def __init__(self):
        super().__init__(settings.PRODUCT_SERVICE_URL)
    
    def list_products(self, params: Optional[Dict] = None) -> Dict[str, Any]:
        """List all products"""
        response = self.get('/products/', params=params)
        # Product service returns {success, message, data, pagination}
        if response.get('success'):
            return {
                'results': response.get('data', []),
                'count': response.get('pagination', {}).get('count', 0),
                'next': self._extract_page(response.get('pagination', {}).get('next')),
                'previous': self._extract_page(response.get('pagination', {}).get('previous')),
            }
        return {'results': [], 'count': 0}

    @staticmethod
    def _extract_page(url: Optional[str]) -> Optional[str]:
        if not url:
            return None
        return parse_qs(urlparse(url).query).get('page', [None])[0]
    
    def get_product(self, product_id: int) -> Dict[str, Any]:
        """Get product detail"""
        response = self.get(f'/products/{product_id}/')
        # Product service returns {success, message, data}
        if response.get('success'):
            return response.get('data', {})
        return {}
    
    def check_stock(self, product_id: int) -> Dict[str, Any]:
        """Check product stock"""
        product = self.get_product(product_id)
        return {'available': product.get('stock', 0)}


class CartServiceClient(APIClient):
    """Client for Cart Service — endpoints: /cart/carts/, /cart/items/"""
    
    def __init__(self):
        super().__init__(settings.CART_SERVICE_URL)
    
    def get_or_create_cart(self, token: str) -> Dict[str, Any]:
        """Get user's active cart, or create one if none exists.
        Returns the cart dict with 'id', 'items', etc."""
        resp = self.get('/cart/carts/', token=token)
        carts = resp.get('data', [])
        active = [c for c in carts if c.get('status') == 'active']
        if active:
            return active[0]
        # No active cart — create one
        create_resp = self.post('/cart/carts/', {}, token=token)
        return create_resp.get('data', create_resp)
    
    def get_cart_items(self, token: str) -> list:
        """Get all cart items for the authenticated user"""
        resp = self.get('/cart/items/', token=token)
        return resp.get('data', [])
    
    def add_to_cart(self, cart_id: int, product_id: int, quantity: int, unit_price: str, token: str) -> Dict[str, Any]:
        """Add item to cart"""
        return self.post('/cart/items/', {
            'cart': cart_id,
            'product_id': product_id,
            'quantity': quantity,
            'unit_price': unit_price
        }, token=token)
    
    def update_cart_item(self, item_id: int, quantity: int, token: str) -> Dict[str, Any]:
        """Update cart item quantity"""
        return self.put(f'/cart/items/{item_id}/', {
            'quantity': quantity
        }, token=token)
    
    def remove_from_cart(self, item_id: int, token: str) -> Dict[str, Any]:
        """Remove item from cart"""
        return self.delete(f'/cart/items/{item_id}/', token=token)


class OrderServiceClient(APIClient):
    """Client for Order Service — endpoints: /orders/"""
    
    def __init__(self):
        super().__init__(settings.ORDER_SERVICE_URL)
    
    def create_order(self, data: Dict[str, Any], token: str) -> Dict[str, Any]:
        """Create new order with order_items"""
        resp = self.post('/orders/', data, token=token)
        if resp.get('success'):
            return resp.get('data', resp)
        return resp
    
    def list_orders(self, token: str) -> Dict[str, Any]:
        """List user orders"""
        resp = self.get('/orders/', token=token)
        if resp.get('success'):
            return {'results': resp.get('data', []), 'count': resp.get('pagination', {}).get('count', 0)}
        return {'results': [], 'count': 0}
    
    def get_order(self, order_id: int, token: str) -> Dict[str, Any]:
        """Get order detail"""
        resp = self.get(f'/orders/{order_id}/', token=token)
        if resp.get('success'):
            return resp.get('data', {})
        return {}


class ShippingServiceClient(APIClient):
    """Client for Shipping Service — endpoints: /shipping/"""
    
    def __init__(self):
        super().__init__(settings.SHIPPING_SERVICE_URL)
    
    def create_shipment(self, order_id: int, address: str, carrier: str, token: str) -> Dict[str, Any]:
        """Create shipment for an order"""
        return self.post('/shipping/', {
            'order_id': order_id,
            'address': address,
            'carrier': carrier,
        }, token=token)
    
    def get_shipment(self, shipment_id: int, token: str) -> Dict[str, Any]:
        """Get shipment detail"""
        return self.get(f'/shipping/{shipment_id}/', token=token)


class PaymentServiceClient(APIClient):
    """Client for Payment Service — endpoints: /payments/"""
    
    def __init__(self):
        super().__init__(settings.PAYMENT_SERVICE_URL)
    
    def create_payment(self, order_id: int, provider: str, token: str) -> Dict[str, Any]:
        """Create payment for an order"""
        return self.post('/payments/', {
            'order_id': order_id,
            'provider': provider,
        }, token=token)
    
    def get_payment(self, payment_id: int, token: str) -> Dict[str, Any]:
        """Get payment detail"""
        return self.get(f'/payments/{payment_id}/', token=token)


class AIServiceClient(APIClient):
    """Client for AI Recommendation and Chatbot Service"""
    
    def __init__(self):
        super().__init__(settings.AI_SERVICE_URL)
        
    def get_smart_recommendations(self, user_id: int, token: str, k: int = 4) -> Dict[str, Any]:
        """Get smart recommendations enriched from other services"""
        try:
            return self.post('/api/v1/smart-recommend', {
                'user_id': user_id,
                'k': k,
                'filter_available': True
            }, token=token)
        except Exception as e:
            print(f"Error calling smart recommendations: {e}")
            return {'success': False, 'data': []}
            
    def get_recommendations(self, user_id: int, k: int = 4) -> Dict[str, Any]:
        """Get basic hybrid recommendations (no enrichment)"""
        try:
            return self.post('/api/v1/recommend', {
                'user_id': user_id,
                'k': k
            })
        except Exception as e:
            print(f"Error calling recommendations: {e}")
            return {'success': False, 'data': []}

    def get_similar_products(self, product_id: int) -> Dict[str, Any]:
        """Get similar products based on knowledge graph"""
        try:
            return self.get(f'/api/v1/similar/{product_id}')
        except Exception as e:
            print(f"Error fetching similar products: {e}")
            return {'success': False, 'data': []}

    def get_query_recommendations(self, query: str, k: int = 4) -> Dict[str, Any]:
        """Get query-based recommendations using RAG"""
        try:
            return self.post('/api/v1/recommend/query', {
                'query': query,
                'k': k
            })
        except Exception as e:
            print(f"Error calling query recommendations: {e}")
            return {'success': False, 'data': []}

    def send_chatbot_query(self, query: str) -> Dict[str, Any]:
        """Get chatbot response (RAG-based)"""
        return self.post('/api/v1/chatbot', {
            'message': query  # AI service expects 'message' field, not 'query'
        })
