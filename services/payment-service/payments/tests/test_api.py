import jwt
from django.conf import settings
from rest_framework.exceptions import NotFound, PermissionDenied, ValidationError
from rest_framework import status
from rest_framework.test import APITestCase
from unittest.mock import patch

from payments.models import Payment


class PaymentApiTests(APITestCase):
    def auth(self, user_id):
        token = jwt.encode(
            {"user_id": user_id, "token_type": "access"},
            settings.JWT_SIGNING_KEY,
            algorithm="HS256",
        )
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    def test_list_payments_requires_authentication(self):
        response = self.client.get("/payments/")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertFalse(response.data["success"])

    def test_list_payments_rejects_invalid_token(self):
        self.client.credentials(HTTP_AUTHORIZATION="Bearer invalid-token")
        response = self.client.get("/payments/")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertFalse(response.data["success"])

    @patch("payment_service.order_client.OrderServiceClient.assert_order_access", return_value={"id": 1, "user_id": 10})
    def test_create_payment_returns_success_envelope(self, mocked_assert):
        self.auth(user_id=10)

        response = self.client.post(
            "/payments/",
            {
                "order_id": 1,
                "amount": "50.00",
                "provider": "stripe",
                "transaction_id": "txn-test-001",
                "status": "pending",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data["success"])
        mocked_assert.assert_called_once()
        self.assertTrue(Payment.objects.filter(transaction_id="txn-test-001").exists())

    @patch("payment_service.order_client.OrderServiceClient.assert_order_access", return_value={"id": 1, "user_id": 10})
    def test_create_payment_with_idempotency_key_replays_existing_payment(self, mocked_assert):
        self.auth(user_id=10)
        payload = {
            "order_id": 1,
            "amount": "50.00",
            "provider": "stripe",
            "transaction_id": "txn-test-idem-001",
            "status": "pending",
        }

        first_response = self.client.post(
            "/payments/",
            payload,
            format="json",
            HTTP_IDEMPOTENCY_KEY="pay-key-001",
        )
        second_response = self.client.post(
            "/payments/",
            payload,
            format="json",
            HTTP_IDEMPOTENCY_KEY="pay-key-001",
        )

        self.assertEqual(first_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(second_response.status_code, status.HTTP_200_OK)
        self.assertEqual(first_response.data["data"]["id"], second_response.data["data"]["id"])
        self.assertEqual(Payment.objects.count(), 1)
        self.assertGreaterEqual(mocked_assert.call_count, 2)

    @patch("payment_service.order_client.OrderServiceClient.assert_orders_access_batch", return_value={1})
    def test_list_payments_filters_by_verified_order_access(self, mocked_assert):
        Payment.objects.create(order_id=1, amount="50.00", provider="stripe", transaction_id="txn-test-002", status="pending")
        self.auth(user_id=10)

        response = self.client.get("/payments/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        self.assertEqual(response.data["pagination"]["count"], 1)
        mocked_assert.assert_called_once()

    @patch("payment_service.order_client.OrderServiceClient.assert_order_access", side_effect=PermissionDenied("You do not have access to this order."))
    def test_create_payment_returns_forbidden_when_order_is_not_owned(self, mocked_assert):
        self.auth(user_id=10)

        response = self.client.post(
            "/payments/",
            {
                "order_id": 1,
                "amount": "50.00",
                "provider": "stripe",
                "transaction_id": "txn-test-003",
                "status": "pending",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertFalse(response.data["success"])
        mocked_assert.assert_called_once()

    @patch("payment_service.order_client.OrderServiceClient.assert_order_access", side_effect=NotFound("Order not found."))
    def test_create_payment_returns_not_found_when_order_missing(self, mocked_assert):
        self.auth(user_id=10)

        response = self.client.post(
            "/payments/",
            {
                "order_id": 999,
                "amount": "50.00",
                "provider": "stripe",
                "transaction_id": "txn-test-004",
                "status": "pending",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertFalse(response.data["success"])
        mocked_assert.assert_called_once()

    @patch("payment_service.order_client.OrderServiceClient.assert_order_access", side_effect=ValidationError({"order_id": "Order service is unavailable."}))
    def test_create_payment_returns_bad_request_when_order_service_unavailable(self, mocked_assert):
        self.auth(user_id=10)

        response = self.client.post(
            "/payments/",
            {
                "order_id": 1,
                "amount": "50.00",
                "provider": "stripe",
                "transaction_id": "txn-test-005",
                "status": "pending",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data["success"])
        self.assertIn("order_id", response.data["errors"])
        mocked_assert.assert_called_once()

    @patch("payment_service.order_client.OrderServiceClient.assert_order_access", return_value={"id": 1, "user_id": 10})
    def test_payment_detail_update_delete_flow(self, mocked_assert):
        payment = Payment.objects.create(order_id=1, amount="50.00", provider="stripe", transaction_id="txn-test-006", status="pending")
        self.auth(user_id=10)

        detail_response = self.client.get(f"/payments/{payment.id}/")
        self.assertEqual(detail_response.status_code, status.HTTP_200_OK)
        self.assertTrue(detail_response.data["success"])

        update_response = self.client.put(
            f"/payments/{payment.id}/",
            {
                "order_id": 1,
                "amount": "65.00",
                "provider": "stripe",
                "transaction_id": "txn-test-006",
                "status": "completed",
            },
            format="json",
        )
        self.assertEqual(update_response.status_code, status.HTTP_200_OK)
        self.assertEqual(update_response.data["data"]["status"], "completed")

        delete_response = self.client.delete(f"/payments/{payment.id}/")
        self.assertEqual(delete_response.status_code, status.HTTP_200_OK)
        self.assertTrue(delete_response.data["success"])
        self.assertFalse(Payment.objects.filter(id=payment.id).exists())
        self.assertGreaterEqual(mocked_assert.call_count, 3)

    @patch("payment_service.order_client.OrderServiceClient.assert_order_access", side_effect=PermissionDenied("You do not have access to this order."))
    def test_payment_detail_returns_forbidden_when_order_verification_fails(self, mocked_assert):
        payment = Payment.objects.create(order_id=1, amount="50.00", provider="stripe", transaction_id="txn-test-007", status="pending")
        self.auth(user_id=10)

        response = self.client.get(f"/payments/{payment.id}/")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertFalse(response.data["success"])
        mocked_assert.assert_called_once()

    @patch("payment_service.order_client.OrderServiceClient.assert_orders_access_batch", side_effect=ValidationError({"order_id": "Order service is unavailable."}))
    def test_payment_list_returns_bad_request_when_order_service_unavailable(self, mocked_assert):
        Payment.objects.create(order_id=1, amount="50.00", provider="stripe", transaction_id="txn-test-008", status="pending")
        self.auth(user_id=10)

        response = self.client.get("/payments/")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data["success"])
        self.assertIn("order_id", response.data["errors"])
        mocked_assert.assert_called_once()
