from django.test import TestCase

from orders.models import Order
from orders.serializers import OrderItemSerializer, OrderSerializer


class OrderSerializerTests(TestCase):
    def test_serializer_accepts_valid_payload_without_user_id(self):
        serializer = OrderSerializer(
            data={
                "status": "pending",
                "total_amount": "120.50",
                "shipping_address": "123 Main St",
            }
        )

        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_serializer_rejects_invalid_status(self):
        serializer = OrderSerializer(
            data={
                "status": "unknown",
                "total_amount": "120.50",
                "shipping_address": "123 Main St",
            }
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn("status", serializer.errors)

    def test_serializer_requires_total_amount(self):
        serializer = OrderSerializer(
            data={
                "status": "pending",
                "shipping_address": "123 Main St",
            }
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn("total_amount", serializer.errors)

    def test_serializer_ignores_read_only_user_id(self):
        serializer = OrderSerializer(
            data={
                "user_id": 999,
                "status": "pending",
                "total_amount": "120.50",
                "shipping_address": "123 Main St",
            }
        )

        self.assertTrue(serializer.is_valid(), serializer.errors)
        self.assertNotIn("user_id", serializer.validated_data)


class OrderItemSerializerTests(TestCase):
    def setUp(self):
        self.order = Order.objects.create(
            user_id=1,
            status="pending",
            total_amount="120.50",
            shipping_address="123 Main St",
        )

    def test_serializer_accepts_valid_payload(self):
        serializer = OrderItemSerializer(
            data={
                "order": self.order.id,
                "product_id": 1001,
                "quantity": 2,
                "unit_price": "19.99",
            }
        )

        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_serializer_requires_product_id(self):
        serializer = OrderItemSerializer(
            data={
                "order": self.order.id,
                "quantity": 2,
                "unit_price": "19.99",
            }
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn("product_id", serializer.errors)

    def test_serializer_rejects_non_positive_quantity(self):
        serializer = OrderItemSerializer(
            data={
                "order": self.order.id,
                "product_id": 1001,
                "quantity": -1,
                "unit_price": "19.99",
            }
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn("quantity", serializer.errors)