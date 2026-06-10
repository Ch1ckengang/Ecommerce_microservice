import jwt
from django.conf import settings
from rest_framework import status
from rest_framework.test import APITestCase

from carts.models import Cart, CartItem


class CartApiTests(APITestCase):
    def auth(self, user_id):
        token = jwt.encode(
            {"user_id": user_id, "token_type": "access"},
            settings.JWT_SIGNING_KEY,
            algorithm="HS256",
        )
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    def test_list_carts_requires_authentication(self):
        response = self.client.get("/cart/carts/")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertFalse(response.data["success"])

    def test_list_carts_rejects_invalid_token(self):
        self.client.credentials(HTTP_AUTHORIZATION="Bearer invalid-token")
        response = self.client.get("/cart/carts/")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertFalse(response.data["success"])

    def test_create_cart_uses_authenticated_user_id(self):
        self.auth(user_id=10)

        response = self.client.post("/cart/carts/", {"status": "active"}, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data["success"])
        self.assertEqual(response.data["data"]["user_id"], 10)
        self.assertEqual(Cart.objects.get(id=response.data["data"]["id"]).user_id, 10)

    def test_user_cannot_read_other_users_cart(self):
        cart = Cart.objects.create(user_id=999, status="active")
        self.auth(user_id=10)

        response = self.client.get(f"/cart/carts/{cart.id}/")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertFalse(response.data["success"])

    def test_user_can_create_cart_item_for_own_cart_only(self):
        own_cart = Cart.objects.create(user_id=10, status="active")
        other_cart = Cart.objects.create(user_id=20, status="active")
        self.auth(user_id=10)

        ok_response = self.client.post(
            "/cart/items/",
            {"cart": own_cart.id, "product_id": 1, "quantity": 2, "unit_price": "9.99"},
            format="json",
        )
        self.assertEqual(ok_response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(CartItem.objects.filter(cart=own_cart).exists())

        forbidden_response = self.client.post(
            "/cart/items/",
            {"cart": other_cart.id, "product_id": 1, "quantity": 1, "unit_price": "9.99"},
            format="json",
        )
        self.assertEqual(forbidden_response.status_code, status.HTTP_403_FORBIDDEN)

    def test_list_carts_filters_by_status_for_authenticated_user(self):
        Cart.objects.create(user_id=10, status="active")
        Cart.objects.create(user_id=10, status="checked_out")
        Cart.objects.create(user_id=20, status="active")
        self.auth(user_id=10)

        response = self.client.get("/cart/carts/?status=active")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        self.assertEqual(response.data["pagination"]["count"], 1)
        self.assertEqual(response.data["data"][0]["status"], "active")
        self.assertEqual(response.data["data"][0]["user_id"], 10)

    def test_update_own_cart_status_returns_success(self):
        cart = Cart.objects.create(user_id=10, status="active")
        self.auth(user_id=10)

        response = self.client.put(
            f"/cart/carts/{cart.id}/",
            {"status": "checked_out"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        self.assertEqual(response.data["data"]["status"], "checked_out")

    def test_delete_own_cart_returns_success(self):
        cart = Cart.objects.create(user_id=10, status="active")
        self.auth(user_id=10)

        response = self.client.delete(f"/cart/carts/{cart.id}/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        self.assertFalse(Cart.objects.filter(id=cart.id).exists())

    def test_get_missing_cart_returns_not_found(self):
        self.auth(user_id=10)

        response = self.client.get("/cart/carts/999999/")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertFalse(response.data["success"])

    def test_list_cart_items_filters_by_product_id(self):
        own_cart = Cart.objects.create(user_id=10, status="active")
        other_cart = Cart.objects.create(user_id=20, status="active")
        CartItem.objects.create(cart=own_cart, product_id=1, quantity=1, unit_price="9.99")
        CartItem.objects.create(cart=own_cart, product_id=2, quantity=1, unit_price="10.99")
        CartItem.objects.create(cart=other_cart, product_id=1, quantity=1, unit_price="9.99")
        self.auth(user_id=10)

        response = self.client.get("/cart/items/?product_id=1")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        self.assertEqual(response.data["pagination"]["count"], 1)
        self.assertEqual(response.data["data"][0]["product_id"], 1)
        self.assertEqual(response.data["data"][0]["cart"], own_cart.id)

    def test_update_cart_item_returns_success(self):
        cart = Cart.objects.create(user_id=10, status="active")
        item = CartItem.objects.create(cart=cart, product_id=1, quantity=1, unit_price="9.99")
        self.auth(user_id=10)

        response = self.client.put(
            f"/cart/items/{item.id}/",
            {"cart": cart.id, "product_id": 1, "quantity": 3, "unit_price": "8.99"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        item.refresh_from_db()
        self.assertEqual(item.quantity, 3)
        self.assertEqual(str(item.unit_price), "8.99")

    def test_user_cannot_move_item_to_other_users_cart(self):
        own_cart = Cart.objects.create(user_id=10, status="active")
        other_cart = Cart.objects.create(user_id=20, status="active")
        item = CartItem.objects.create(cart=own_cart, product_id=1, quantity=1, unit_price="9.99")
        self.auth(user_id=10)

        response = self.client.put(
            f"/cart/items/{item.id}/",
            {"cart": other_cart.id, "product_id": 1, "quantity": 1, "unit_price": "9.99"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertFalse(response.data["success"])

    def test_delete_cart_item_returns_success(self):
        cart = Cart.objects.create(user_id=10, status="active")
        item = CartItem.objects.create(cart=cart, product_id=1, quantity=1, unit_price="9.99")
        self.auth(user_id=10)

        response = self.client.delete(f"/cart/items/{item.id}/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        self.assertFalse(CartItem.objects.filter(id=item.id).exists())

    def test_get_missing_cart_item_returns_not_found(self):
        self.auth(user_id=10)

        response = self.client.get("/cart/items/999999/")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertFalse(response.data["success"])
