from django.test import TestCase

from carts.models import Cart
from carts.serializers import CartItemSerializer, CartSerializer


class CartSerializerTests(TestCase):
    def test_serializer_accepts_valid_payload_without_user_id(self):
        serializer = CartSerializer(
            data={
                "status": "active",
            }
        )

        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_serializer_rejects_invalid_status(self):
        serializer = CartSerializer(
            data={
                "status": "invalid-status",
            }
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn("status", serializer.errors)

    def test_serializer_ignores_read_only_user_id(self):
        serializer = CartSerializer(
            data={
                "user_id": 999,
                "status": "active",
            }
        )

        self.assertTrue(serializer.is_valid(), serializer.errors)
        self.assertNotIn("user_id", serializer.validated_data)


class CartItemSerializerTests(TestCase):
    def setUp(self):
        self.cart = Cart.objects.create(user_id=1, status="active")

    def test_serializer_accepts_valid_payload(self):
        serializer = CartItemSerializer(
            data={
                "cart": self.cart.id,
                "product_id": 1001,
                "quantity": 2,
                "unit_price": "19.99",
            }
        )

        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_serializer_requires_product_id(self):
        serializer = CartItemSerializer(
            data={
                "cart": self.cart.id,
                "quantity": 2,
                "unit_price": "19.99",
            }
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn("product_id", serializer.errors)

    def test_serializer_rejects_non_positive_quantity(self):
        serializer = CartItemSerializer(
            data={
                "cart": self.cart.id,
                "product_id": 1001,
                "quantity": -1,
                "unit_price": "19.99",
            }
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn("quantity", serializer.errors)