import json
import os
import time
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from rest_framework.exceptions import NotFound, PermissionDenied, ValidationError


class OrderServiceClient:
    @staticmethod
    def _request_with_retry(request: Request):
        max_retries = max(1, int(os.getenv("ORDER_SERVICE_MAX_RETRIES", "3")))
        retry_backoff = float(os.getenv("ORDER_SERVICE_RETRY_BACKOFF", "0.1"))

        last_error = None
        for attempt in range(max_retries):
            try:
                with urlopen(request, timeout=5) as response:
                    return json.loads(response.read().decode("utf-8"))
            except HTTPError as exc:
                if exc.code >= 500 and attempt < max_retries - 1:
                    last_error = exc
                    time.sleep(retry_backoff * (2 ** attempt))
                    continue
                raise
            except URLError as exc:
                last_error = exc
                if attempt < max_retries - 1:
                    time.sleep(retry_backoff * (2 ** attempt))
                    continue
                raise

        raise last_error

    @staticmethod
    def assert_order_access(order_id: int, token: str):
        base_url = os.getenv("ORDER_SERVICE_URL", "http://order-service:8000")
        request = Request(
            f"{base_url}/orders/{order_id}/",
            headers={
                "Authorization": f"Bearer {token}",
                "Accept": "application/json",
            },
        )

        try:
            payload = OrderServiceClient._request_with_retry(request)
        except HTTPError as exc:
            if exc.code == 404:
                raise NotFound("Order not found.") from exc
            if exc.code in {401, 403}:
                raise PermissionDenied("You do not have access to this order.") from exc
            raise ValidationError({"order_id": "Failed to verify order ownership."}) from exc
        except URLError as exc:
            raise ValidationError({"order_id": "Order service is unavailable."}) from exc

        data = payload.get("data", {})
        if data.get("id") != order_id:
            raise ValidationError({"order_id": "Order verification returned unexpected data."})

        return data

    @staticmethod
    def assert_orders_access_batch(order_ids: list[int], token: str) -> set[int]:
        if not order_ids:
            return set()

        base_url = os.getenv("ORDER_SERVICE_URL", "http://order-service:8000")
        request = Request(
            f"{base_url}/orders/ownership/verify-batch/",
            data=json.dumps({"order_ids": order_ids}).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {token}",
                "Accept": "application/json",
                "Content-Type": "application/json",
            },
            method="POST",
        )

        try:
            payload = OrderServiceClient._request_with_retry(request)
        except HTTPError as exc:
            if exc.code in {401, 403}:
                raise PermissionDenied("You do not have access to this order.") from exc
            raise ValidationError({"order_id": "Failed to verify order ownership."}) from exc
        except URLError as exc:
            raise ValidationError({"order_id": "Order service is unavailable."}) from exc

        data = payload.get("data", {})
        accessible_order_ids = data.get("accessible_order_ids", [])
        if not isinstance(accessible_order_ids, list):
            raise ValidationError({"order_id": "Invalid order ownership response."})

        try:
            return {int(order_id) for order_id in accessible_order_ids}
        except (TypeError, ValueError) as exc:
            raise ValidationError({"order_id": "Invalid order ownership response."}) from exc
