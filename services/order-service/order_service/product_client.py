import os
import time
import requests
from rest_framework.exceptions import ValidationError


class ProductServiceClient:
    """Client to communicate with Product Service"""
    
    def __init__(self):
        self.base_url = os.getenv("PRODUCT_SERVICE_URL", "http://product-service:8000")
        self.service_token = os.getenv("PRODUCT_SERVICE_TOKEN", "")
        self.max_retries = max(1, int(os.getenv("PRODUCT_SERVICE_MAX_RETRIES", "3")))
        self.retry_backoff = float(os.getenv("PRODUCT_SERVICE_RETRY_BACKOFF", "0.1"))

    def _headers(self):
        headers = {}
        if self.service_token:
            headers["X-Service-Token"] = self.service_token
        return headers

    def _post_with_retry(self, path, payload):
        last_error = None
        for attempt in range(self.max_retries):
            try:
                response = requests.post(
                    f"{self.base_url}{path}",
                    json=payload,
                    headers=self._headers(),
                    timeout=5,
                )
                if response.status_code >= 500:
                    raise requests.RequestException(f"Product service returned {response.status_code}")
                return response
            except requests.RequestException as exc:
                last_error = exc
                if attempt == self.max_retries - 1:
                    raise
                time.sleep(self.retry_backoff * (2 ** attempt))

        raise last_error

    def _get_with_retry(self, path):
        last_error = None
        for attempt in range(self.max_retries):
            try:
                response = requests.get(
                    f"{self.base_url}{path}",
                    headers=self._headers(),
                    timeout=5,
                )
                if response.status_code >= 500:
                    raise requests.RequestException(f"Product service returned {response.status_code}")
                return response
            except requests.RequestException as exc:
                last_error = exc
                if attempt == self.max_retries - 1:
                    raise
                time.sleep(self.retry_backoff * (2 ** attempt))

        raise last_error

    def get_product(self, product_id):
        try:
            response = self._get_with_retry(f"/products/{product_id}/")
            if response.status_code == 200:
                payload = response.json()
                return payload.get("data", {})
            raise ValidationError({"order_items": f"Product {product_id} not found."})
        except requests.RequestException as e:
            raise ValidationError(f"Product service unavailable: {str(e)}")
    
    def check_stock(self, products):
        """
        Check stock availability for products
        products: [{"product_id": 1, "quantity": 2}, ...]
        """
        try:
            response = self._post_with_retry(
                "/products/stock/check/",
                {"products": products},
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get("data", {})
            else:
                raise ValidationError("Failed to check product stock")
        except requests.RequestException as e:
            raise ValidationError(f"Product service unavailable: {str(e)}")
    
    def reserve_stock(self, products):
        """
        Reserve stock for products
        products: [{"product_id": 1, "quantity": 2}, ...]
        """
        try:
            response = self._post_with_retry(
                "/products/stock/reserve/",
                {"products": products},
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get("data", {})
            else:
                raise ValidationError("Failed to reserve product stock")
        except requests.RequestException as e:
            raise ValidationError(f"Product service unavailable: {str(e)}")
    
    def release_stock(self, products):
        """
        Release reserved stock
        products: [{"product_id": 1, "quantity": 2}, ...]
        """
        try:
            response = self._post_with_retry(
                "/products/stock/release/",
                {"products": products},
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get("data", {})
            else:
                # Don't raise error on release failure, just log
                return {"success": False, "message": "Failed to release stock"}
        except requests.RequestException:
            # Don't raise error on release failure
            return {"success": False, "message": "Product service unavailable"}
