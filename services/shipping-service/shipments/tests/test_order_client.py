import os
from unittest.mock import MagicMock, patch
from urllib.error import URLError

from django.test import TestCase

from shipping_service.order_client import OrderServiceClient


class ShippingOrderClientRetryTests(TestCase):
    @patch.dict(os.environ, {"ORDER_SERVICE_MAX_RETRIES": "2", "ORDER_SERVICE_RETRY_BACKOFF": "0"}, clear=False)
    @patch("shipping_service.order_client.urlopen")
    def test_assert_order_access_retries_once_on_urlerror(self, mock_urlopen):
        success_cm = MagicMock()
        success_cm.__enter__.return_value.read.return_value = b'{"data": {"id": 1, "user_id": 10}}'
        success_cm.__exit__.return_value = False

        mock_urlopen.side_effect = [URLError("temporary"), success_cm]

        result = OrderServiceClient.assert_order_access(order_id=1, token="token")

        self.assertEqual(result["id"], 1)
        self.assertEqual(mock_urlopen.call_count, 2)
