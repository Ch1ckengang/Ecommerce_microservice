import jwt
from django.conf import settings
from rest_framework import status
from rest_framework.test import APITestCase
from unittest.mock import patch

from orders.models import Order, OrderItem


class OrderApiTests(APITestCase):
    def auth(self, user_id):
        token = jwt.encode(
            {"user_id": user_id, "token_type": "access"},
            settings.JWT_SIGNING_KEY,
            algorithm="HS256",
        )
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    def test_list_orders_requires_authentication(self):
        response = self.client.get("/orders/")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertFalse(response.data["success"])

    def test_list_orders_rejects_invalid_token(self):
        self.client.credentials(HTTP_AUTHORIZATION="Bearer invalid-token")
        response = self.client.get("/orders/")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertFalse(response.data["success"])

    def test_create_order_uses_authenticated_user_id(self):
        self.auth(user_id=11)

        response = self.client.post(
            "/orders/",
            {
                "status": "pending",
                "total_amount": "19.99",
                "shipping_address": "123 Test Street",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["data"]["user_id"], 11)
        self.assertEqual(Order.objects.get(id=response.data["data"]["id"]).user_id, 11)

    @patch("orders.services.ProductServiceClient")
    def test_create_order_with_items_checks_and_reserves_stock(self, mock_client_cls):
        mock_client = mock_client_cls.return_value
        mock_client.check_stock.return_value = {"available": True, "unavailable": []}
        mock_client.reserve_stock.return_value = {"success": True}

        self.auth(user_id=11)
        response = self.client.post(
            "/orders/",
            {
                "status": "pending",
                "total_amount": "39.98",
                "shipping_address": "123 Test Street",
                "order_items": [
                    {"product_id": 101, "quantity": 2, "unit_price": "9.99"},
                    {"product_id": 202, "quantity": 1, "unit_price": "20.00"},
                ],
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data["success"])
        order_id = response.data["data"]["id"]
        self.assertEqual(OrderItem.objects.filter(order_id=order_id).count(), 2)
        mock_client.check_stock.assert_called_once()
        mock_client.reserve_stock.assert_called_once()
        mock_client.release_stock.assert_not_called()

    @patch("orders.services.ProductServiceClient")
    def test_create_order_with_items_rejects_when_stock_unavailable(self, mock_client_cls):
        mock_client = mock_client_cls.return_value
        mock_client.check_stock.return_value = {
            "available": False,
            "unavailable": [{"name": "USB-C Hub", "requested": 10, "available": 1}],
        }

        self.auth(user_id=11)
        response = self.client.post(
            "/orders/",
            {
                "status": "pending",
                "total_amount": "99.99",
                "shipping_address": "123 Test Street",
                "order_items": [{"product_id": 101, "quantity": 10, "unit_price": "9.99"}],
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data["success"])
        self.assertIn("order_items", response.data["errors"])
        self.assertEqual(Order.objects.count(), 0)
        self.assertEqual(OrderItem.objects.count(), 0)
        mock_client.reserve_stock.assert_not_called()

    @patch("orders.services.ProductServiceClient")
    def test_create_order_with_idempotency_key_replays_existing_order(self, mock_client_cls):
        mock_client = mock_client_cls.return_value
        mock_client.check_stock.return_value = {"available": True, "unavailable": []}
        mock_client.reserve_stock.return_value = {"success": True}

        self.auth(user_id=11)
        payload = {
            "status": "pending",
            "total_amount": "39.98",
            "shipping_address": "123 Test Street",
            "order_items": [
                {"product_id": 101, "quantity": 2, "unit_price": "9.99"},
            ],
        }

        first_response = self.client.post(
            "/orders/",
            payload,
            format="json",
            HTTP_IDEMPOTENCY_KEY="ord-key-001",
        )
        second_response = self.client.post(
            "/orders/",
            payload,
            format="json",
            HTTP_IDEMPOTENCY_KEY="ord-key-001",
        )

        self.assertEqual(first_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(second_response.status_code, status.HTTP_200_OK)
        self.assertEqual(first_response.data["data"]["id"], second_response.data["data"]["id"])
        self.assertEqual(Order.objects.count(), 1)
        self.assertEqual(OrderItem.objects.count(), 1)
        mock_client.check_stock.assert_called_once()
        mock_client.reserve_stock.assert_called_once()

    def test_user_cannot_read_other_users_order(self):
        order = Order.objects.create(
            user_id=999,
            status="pending",
            total_amount="19.99",
            shipping_address="123 Test Street",
        )
        self.auth(user_id=11)

        response = self.client.get(f"/orders/{order.id}/")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertFalse(response.data["success"])

    def test_user_can_create_order_item_for_own_order_only(self):
        own_order = Order.objects.create(
            user_id=11,
            status="pending",
            total_amount="19.99",
            shipping_address="123 Test Street",
        )
        other_order = Order.objects.create(
            user_id=22,
            status="pending",
            total_amount="19.99",
            shipping_address="456 Test Street",
        )
        self.auth(user_id=11)

        ok_response = self.client.post(
            "/orders/items/",
            {"order": own_order.id, "product_id": 1, "quantity": 2, "unit_price": "9.99"},
            format="json",
        )
        self.assertEqual(ok_response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(OrderItem.objects.filter(order=own_order).exists())

        forbidden_response = self.client.post(
            "/orders/items/",
            {"order": other_order.id, "product_id": 1, "quantity": 1, "unit_price": "9.99"},
            format="json",
        )
        self.assertEqual(forbidden_response.status_code, status.HTTP_403_FORBIDDEN)

    def test_list_orders_filters_by_status_for_authenticated_user(self):
        Order.objects.create(user_id=11, status="pending", total_amount="10.00", shipping_address="A")
        Order.objects.create(user_id=11, status="paid", total_amount="20.00", shipping_address="B")
        Order.objects.create(user_id=22, status="pending", total_amount="30.00", shipping_address="C")
        self.auth(user_id=11)

        response = self.client.get("/orders/?status=pending")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        self.assertEqual(response.data["pagination"]["count"], 1)
        self.assertEqual(response.data["data"][0]["status"], "pending")
        self.assertEqual(response.data["data"][0]["user_id"], 11)

    def test_update_own_order_returns_success(self):
        order = Order.objects.create(
            user_id=11,
            status="pending",
            total_amount="19.99",
            shipping_address="123 Test Street",
        )
        self.auth(user_id=11)

        response = self.client.put(
            f"/orders/{order.id}/",
            {
                "status": "paid",
                "total_amount": "19.99",
                "shipping_address": "123 Updated Street",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        self.assertEqual(response.data["data"]["status"], "paid")

    def test_delete_own_order_returns_success(self):
        order = Order.objects.create(
            user_id=11,
            status="pending",
            total_amount="19.99",
            shipping_address="123 Test Street",
        )
        self.auth(user_id=11)

        response = self.client.delete(f"/orders/{order.id}/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        self.assertFalse(Order.objects.filter(id=order.id).exists())

    def test_get_missing_order_returns_not_found(self):
        self.auth(user_id=11)

        response = self.client.get("/orders/999999/")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertFalse(response.data["success"])

    def test_list_order_items_filters_by_product_id(self):
        own_order = Order.objects.create(
            user_id=11,
            status="pending",
            total_amount="19.99",
            shipping_address="123 Test Street",
        )
        other_order = Order.objects.create(
            user_id=22,
            status="pending",
            total_amount="19.99",
            shipping_address="456 Test Street",
        )
        OrderItem.objects.create(order=own_order, product_id=1, quantity=1, unit_price="9.99")
        OrderItem.objects.create(order=own_order, product_id=2, quantity=1, unit_price="9.99")
        OrderItem.objects.create(order=other_order, product_id=1, quantity=1, unit_price="9.99")
        self.auth(user_id=11)

        response = self.client.get("/orders/items/?product_id=1")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        self.assertEqual(response.data["pagination"]["count"], 1)
        self.assertEqual(response.data["data"][0]["product_id"], 1)
        self.assertEqual(response.data["data"][0]["order"], own_order.id)

    def test_update_order_item_returns_success(self):
        order = Order.objects.create(
            user_id=11,
            status="pending",
            total_amount="19.99",
            shipping_address="123 Test Street",
        )
        item = OrderItem.objects.create(order=order, product_id=1, quantity=1, unit_price="9.99")
        self.auth(user_id=11)

        response = self.client.put(
            f"/orders/items/{item.id}/",
            {"order": order.id, "product_id": 1, "quantity": 3, "unit_price": "8.99"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        item.refresh_from_db()
        self.assertEqual(item.quantity, 3)
        self.assertEqual(str(item.unit_price), "8.99")

    def test_user_cannot_move_item_to_other_users_order(self):
        own_order = Order.objects.create(
            user_id=11,
            status="pending",
            total_amount="19.99",
            shipping_address="123 Test Street",
        )
        other_order = Order.objects.create(
            user_id=22,
            status="pending",
            total_amount="19.99",
            shipping_address="456 Test Street",
        )
        item = OrderItem.objects.create(order=own_order, product_id=1, quantity=1, unit_price="9.99")
        self.auth(user_id=11)

        response = self.client.put(
            f"/orders/items/{item.id}/",
            {"order": other_order.id, "product_id": 1, "quantity": 1, "unit_price": "9.99"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertFalse(response.data["success"])

    def test_delete_order_item_returns_success(self):
        order = Order.objects.create(
            user_id=11,
            status="pending",
            total_amount="19.99",
            shipping_address="123 Test Street",
        )
        item = OrderItem.objects.create(order=order, product_id=1, quantity=1, unit_price="9.99")
        self.auth(user_id=11)

        response = self.client.delete(f"/orders/items/{item.id}/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        self.assertFalse(OrderItem.objects.filter(id=item.id).exists())

    def test_get_missing_order_item_returns_not_found(self):
        self.auth(user_id=11)

        response = self.client.get("/orders/items/999999/")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertFalse(response.data["success"])

    def test_batch_order_access_returns_only_accessible_order_ids(self):
        own_order_1 = Order.objects.create(user_id=11, status="pending", total_amount="10.00", shipping_address="A")
        own_order_2 = Order.objects.create(user_id=11, status="paid", total_amount="20.00", shipping_address="B")
        other_order = Order.objects.create(user_id=22, status="pending", total_amount="30.00", shipping_address="C")
        self.auth(user_id=11)

        response = self.client.post(
            "/orders/ownership/verify-batch/",
            {"order_ids": [own_order_1.id, other_order.id, own_order_2.id]},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        self.assertEqual(response.data["data"]["accessible_order_ids"], [own_order_1.id, own_order_2.id])
        self.assertEqual(response.data["data"]["requested_count"], 3)
        self.assertEqual(response.data["data"]["accessible_count"], 2)

    def test_batch_order_access_returns_empty_for_empty_input(self):
        self.auth(user_id=11)

        response = self.client.post(
            "/orders/ownership/verify-batch/",
            {"order_ids": []},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        self.assertEqual(response.data["data"]["accessible_order_ids"], [])
        self.assertEqual(response.data["data"]["requested_count"], 0)
        self.assertEqual(response.data["data"]["accessible_count"], 0)

    def test_batch_order_access_rejects_invalid_payload(self):
        self.auth(user_id=11)

        response = self.client.post(
            "/orders/ownership/verify-batch/",
            {"order_ids": "not-a-list"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data["success"])
        self.assertIn("order_ids", response.data["errors"])
