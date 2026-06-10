from django.test import TestCase
from rest_framework.exceptions import NotFound

from carts.models import Cart, CartItem
from carts.services import CartItemService, CartService


class CartServiceTests(TestCase):
    def setUp(self):
        self.cart_1 = Cart.objects.create(user_id=1, status="active")
        self.cart_2 = Cart.objects.create(user_id=2, status="checked_out")

    def test_list_carts_filters_by_user_id(self):
        queryset = CartService.list_carts({"user_id": 1})

        self.assertEqual(queryset.count(), 1)
        self.assertEqual(queryset.first().id, self.cart_1.id)

    def test_list_carts_filters_by_status(self):
        queryset = CartService.list_carts({"status": "checked_out"})

        self.assertEqual(queryset.count(), 1)
        self.assertEqual(queryset.first().id, self.cart_2.id)

    def test_get_cart_raises_not_found_for_missing_id(self):
        with self.assertRaises(NotFound):
            CartService.get_cart(999999)

    def test_update_cart_persists_changes(self):
        CartService.update_cart(self.cart_1, {"status": "checked_out"})
        self.cart_1.refresh_from_db()

        self.assertEqual(self.cart_1.status, "checked_out")

    def test_delete_cart_removes_record(self):
        CartService.delete_cart(self.cart_1)

        self.assertFalse(Cart.objects.filter(id=self.cart_1.id).exists())


class CartItemServiceTests(TestCase):
    def setUp(self):
        self.cart_1 = Cart.objects.create(user_id=1, status="active")
        self.cart_2 = Cart.objects.create(user_id=2, status="active")
        self.item_1 = CartItem.objects.create(cart=self.cart_1, product_id=101, quantity=2, unit_price="10.00")
        self.item_2 = CartItem.objects.create(cart=self.cart_2, product_id=102, quantity=1, unit_price="20.00")

    def test_list_items_filters_by_cart_id(self):
        queryset = CartItemService.list_items({"cart_id": self.cart_1.id})

        self.assertEqual(queryset.count(), 1)
        self.assertEqual(queryset.first().id, self.item_1.id)

    def test_list_items_filters_by_product_id(self):
        queryset = CartItemService.list_items({"product_id": 102})

        self.assertEqual(queryset.count(), 1)
        self.assertEqual(queryset.first().id, self.item_2.id)

    def test_get_item_raises_not_found_for_missing_id(self):
        with self.assertRaises(NotFound):
            CartItemService.get_item(999999)

    def test_update_item_persists_changes(self):
        CartItemService.update_item(self.item_1, {"quantity": 5, "unit_price": "15.50"})
        self.item_1.refresh_from_db()

        self.assertEqual(self.item_1.quantity, 5)
        self.assertEqual(str(self.item_1.unit_price), "15.50")

    def test_delete_item_removes_record(self):
        CartItemService.delete_item(self.item_1)

        self.assertFalse(CartItem.objects.filter(id=self.item_1.id).exists())