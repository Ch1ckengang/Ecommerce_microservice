from django.test import TestCase
from rest_framework.exceptions import NotFound
from unittest.mock import patch

from orders.models import Order, OrderItem
from orders.services import OrderItemService, OrderService


class OrderServiceTests(TestCase):
    def setUp(self):
        self.order_1 = Order.objects.create(
            user_id=1,
            status="pending",
            total_amount="100.00",
            shipping_address="123 Main St",
        )
        self.order_2 = Order.objects.create(
            user_id=2,
            status="paid",
            total_amount="50.00",
            shipping_address="456 Main St",
        )

    def test_list_orders_filters_by_user_id(self):
        queryset = OrderService.list_orders({"user_id": 1})

        self.assertEqual(queryset.count(), 1)
        self.assertEqual(queryset.first().id, self.order_1.id)

    def test_list_orders_filters_by_status(self):
        queryset = OrderService.list_orders({"status": "paid"})

        self.assertEqual(queryset.count(), 1)
        self.assertEqual(queryset.first().id, self.order_2.id)

    def test_get_order_raises_not_found_for_missing_id(self):
        with self.assertRaises(NotFound):
            OrderService.get_order(999999)

    def test_update_order_persists_changes(self):
        OrderService.update_order(self.order_1, {"status": "cancelled", "total_amount": "10.00"})
        self.order_1.refresh_from_db()

        self.assertEqual(self.order_1.status, "cancelled")
        self.assertEqual(str(self.order_1.total_amount), "10.00")

    def test_delete_order_removes_record(self):
        OrderService.delete_order(self.order_1)

        self.assertFalse(Order.objects.filter(id=self.order_1.id).exists())

    def test_get_accessible_order_ids_preserves_input_order(self):
        self.assertEqual(
            OrderService.get_accessible_order_ids(1, [self.order_2.id, self.order_1.id]),
            [self.order_1.id],
        )

    def test_get_accessible_order_ids_dedupes_ids(self):
        self.assertEqual(
            OrderService.get_accessible_order_ids(1, [self.order_1.id, self.order_1.id, self.order_1.id]),
            [self.order_1.id],
        )

    def test_get_accessible_order_ids_returns_empty_for_empty_input(self):
        self.assertEqual(OrderService.get_accessible_order_ids(1, []), [])

    @patch("orders.services.OrderItem.objects.bulk_create", side_effect=RuntimeError("db failure"))
    @patch("orders.services.ProductServiceClient")
    def test_create_order_with_stock_validation_releases_stock_when_item_write_fails(self, mock_client_cls, _mock_bulk):
        mock_client = mock_client_cls.return_value
        mock_client.check_stock.return_value = {"available": True, "unavailable": []}
        mock_client.reserve_stock.return_value = {"success": True}
        payload = {
            "user_id": 1,
            "status": "pending",
            "total_amount": "100.00",
            "shipping_address": "123 Main St",
        }
        items = [{"product_id": 1, "quantity": 2, "unit_price": "10.00"}]

        with self.assertRaises(RuntimeError):
            OrderService.create_order_with_stock_validation(payload, items)

        mock_client.release_stock.assert_called_once_with([{"product_id": 1, "quantity": 2}])


class OrderItemServiceTests(TestCase):
    def setUp(self):
        self.order_1 = Order.objects.create(
            user_id=1,
            status="pending",
            total_amount="100.00",
            shipping_address="123 Main St",
        )
        self.order_2 = Order.objects.create(
            user_id=2,
            status="pending",
            total_amount="150.00",
            shipping_address="456 Main St",
        )
        self.item_1 = OrderItem.objects.create(order=self.order_1, product_id=101, quantity=2, unit_price="25.00")
        self.item_2 = OrderItem.objects.create(order=self.order_2, product_id=102, quantity=1, unit_price="30.00")

    def test_list_items_filters_by_order_id(self):
        queryset = OrderItemService.list_items({"order_id": self.order_1.id})

        self.assertEqual(queryset.count(), 1)
        self.assertEqual(queryset.first().id, self.item_1.id)

    def test_list_items_filters_by_product_id(self):
        queryset = OrderItemService.list_items({"product_id": 102})

        self.assertEqual(queryset.count(), 1)
        self.assertEqual(queryset.first().id, self.item_2.id)

    def test_get_item_raises_not_found_for_missing_id(self):
        with self.assertRaises(NotFound):
            OrderItemService.get_item(999999)

    def test_update_item_persists_changes(self):
        OrderItemService.update_item(self.item_1, {"quantity": 5, "unit_price": "99.99"})
        self.item_1.refresh_from_db()

        self.assertEqual(self.item_1.quantity, 5)
        self.assertEqual(str(self.item_1.unit_price), "99.99")

    def test_delete_item_removes_record(self):
        OrderItemService.delete_item(self.item_1)

        self.assertFalse(OrderItem.objects.filter(id=self.item_1.id).exists())