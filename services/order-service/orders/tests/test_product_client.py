import os
from unittest.mock import Mock, patch

import requests
from django.test import TestCase

from order_service.product_client import ProductServiceClient


class ProductServiceClientRetryTests(TestCase):
    @patch.dict(os.environ, {"PRODUCT_SERVICE_MAX_RETRIES": "2", "PRODUCT_SERVICE_RETRY_BACKOFF": "0"}, clear=False)
    @patch("order_service.product_client.requests.post")
    def test_check_stock_retries_once_on_transient_error(self, mock_post):
        success_response = Mock()
        success_response.status_code = 200
        success_response.json.return_value = {"data": {"available": True, "unavailable": []}}
        mock_post.side_effect = [requests.RequestException("temporary"), success_response]

        client = ProductServiceClient()
        result = client.check_stock([{"product_id": 1, "quantity": 1}])

        self.assertTrue(result["available"])
        self.assertEqual(mock_post.call_count, 2)
