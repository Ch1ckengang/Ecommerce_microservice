from rest_framework import status
from rest_framework.test import APITestCase
from django.test import override_settings

from products.models import Category, Product


class ProductApiTests(APITestCase):
    def test_create_category_returns_success_envelope(self):
        response = self.client.post(
            "/products/categories/",
            {"name": "Electronics", "description": "Devices and gadgets"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data["success"])
        self.assertEqual(response.data["data"]["name"], "Electronics")
        self.assertTrue(Category.objects.filter(name="Electronics").exists())

    def test_list_categories_supports_search_filter(self):
        Category.objects.create(name="Electronics", description="Devices")
        Category.objects.create(name="Books", description="Reading")

        response = self.client.get("/products/categories/?search=book")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        self.assertEqual(response.data["pagination"]["count"], 1)
        self.assertEqual(response.data["data"][0]["name"], "Books")

    def test_create_product_and_fetch_detail(self):
        category = Category.objects.create(name="Electronics", description="Devices")

        create_response = self.client.post(
            "/products/",
            {
                "category_id": category.id,
                "name": "USB-C Hub",
                "description": "Multiport adapter",
                "price": "59.99",
                "stock": 20,
                "sku": "USBHUB-001",
                "is_active": True,
            },
            format="json",
        )

        self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(create_response.data["success"])
        product_id = create_response.data["data"]["id"]
        self.assertTrue(Product.objects.filter(id=product_id).exists())

        detail_response = self.client.get(f"/products/{product_id}/")

        self.assertEqual(detail_response.status_code, status.HTTP_200_OK)
        self.assertTrue(detail_response.data["success"])
        self.assertEqual(detail_response.data["data"]["name"], "USB-C Hub")
        self.assertEqual(detail_response.data["data"]["category"]["id"], category.id)

    def test_list_products_supports_category_and_is_active_filters(self):
        category = Category.objects.create(name="Electronics", description="Devices")
        Product.objects.create(
            category=category,
            name="Active Product",
            description="Visible",
            price="9.99",
            stock=5,
            sku="ACTIVE-001",
            is_active=True,
        )
        Product.objects.create(
            category=category,
            name="Inactive Product",
            description="Hidden",
            price="19.99",
            stock=0,
            sku="INACTIVE-001",
            is_active=False,
        )

        response = self.client.get(f"/products/?category={category.id}&is_active=true")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        self.assertEqual(response.data["pagination"]["count"], 1)
        self.assertEqual(response.data["data"][0]["sku"], "ACTIVE-001")

    def test_list_products_rejects_invalid_is_active_filter(self):
        response = self.client.get("/products/?is_active=maybe")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data["success"])
        self.assertIn("is_active", response.data["errors"])

    def test_list_products_supports_min_max_price_filters(self):
        category = Category.objects.create(name="Electronics", description="Devices")
        Product.objects.create(
            category=category,
            name="Cheap Product",
            description="Budget",
            price="9.99",
            stock=10,
            sku="CHEAP-001",
            is_active=True,
        )
        Product.objects.create(
            category=category,
            name="Mid Product",
            description="Middle",
            price="39.99",
            stock=10,
            sku="MID-001",
            is_active=True,
        )
        Product.objects.create(
            category=category,
            name="Premium Product",
            description="High-end",
            price="99.99",
            stock=10,
            sku="PREMIUM-001",
            is_active=True,
        )

        response = self.client.get("/products/?min_price=20&max_price=50")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        self.assertEqual(response.data["pagination"]["count"], 1)
        self.assertEqual(response.data["data"][0]["sku"], "MID-001")

    def test_list_products_rejects_invalid_min_price(self):
        response = self.client.get("/products/?min_price=not-a-number")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data["success"])
        self.assertIn("min_price", response.data["errors"])

    def test_list_products_rejects_invalid_max_price(self):
        response = self.client.get("/products/?max_price=abc")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data["success"])
        self.assertIn("max_price", response.data["errors"])

    def test_update_category_returns_success_envelope(self):
        category = Category.objects.create(name="Electronics", description="Devices")

        response = self.client.put(
            f"/products/categories/{category.id}/",
            {"name": "Consumer Electronics", "description": "Updated description"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        self.assertEqual(response.data["data"]["name"], "Consumer Electronics")
        category.refresh_from_db()
        self.assertEqual(category.name, "Consumer Electronics")

    def test_update_category_rejects_duplicate_name(self):
        Category.objects.create(name="Electronics", description="Devices")
        books = Category.objects.create(name="Books", description="Reading")

        response = self.client.put(
            f"/products/categories/{books.id}/",
            {"name": "Electronics", "description": "Reading"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data["success"])
        self.assertIn("name", response.data["errors"])

    def test_delete_category_returns_success_envelope(self):
        category = Category.objects.create(name="Books", description="Reading")

        response = self.client.delete(f"/products/categories/{category.id}/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        self.assertFalse(Category.objects.filter(id=category.id).exists())

    def test_delete_category_with_products_returns_validation_error(self):
        category = Category.objects.create(name="Electronics", description="Devices")
        Product.objects.create(
            category=category,
            name="USB-C Hub",
            description="Adapter",
            price="59.99",
            stock=20,
            sku="USBHUB-001",
            is_active=True,
        )

        response = self.client.delete(f"/products/categories/{category.id}/")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data["success"])
        self.assertIn("category", response.data["errors"])

    def test_get_missing_category_returns_not_found_envelope(self):
        response = self.client.get("/products/categories/999999/")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertFalse(response.data["success"])

    def test_update_product_returns_success_envelope(self):
        category = Category.objects.create(name="Electronics", description="Devices")
        product = Product.objects.create(
            category=category,
            name="USB-C Hub",
            description="Adapter",
            price="59.99",
            stock=20,
            sku="USBHUB-001",
            is_active=True,
        )

        response = self.client.put(
            f"/products/{product.id}/",
            {
                "category_id": category.id,
                "name": "USB-C Hub Pro",
                "description": "Updated adapter",
                "price": "79.99",
                "stock": 15,
                "sku": "USBHUB-001",
                "is_active": True,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        self.assertEqual(response.data["data"]["name"], "USB-C Hub Pro")
        product.refresh_from_db()
        self.assertEqual(str(product.price), "79.99")
        self.assertEqual(product.stock, 15)

    def test_delete_product_returns_success_envelope(self):
        category = Category.objects.create(name="Electronics", description="Devices")
        product = Product.objects.create(
            category=category,
            name="USB-C Hub",
            description="Adapter",
            price="59.99",
            stock=20,
            sku="USBHUB-001",
            is_active=True,
        )

        response = self.client.delete(f"/products/{product.id}/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        self.assertFalse(Product.objects.filter(id=product.id).exists())

    def test_get_missing_product_returns_not_found_envelope(self):
        response = self.client.get("/products/999999/")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertFalse(response.data["success"])

    @override_settings(INTERNAL_SERVICE_TOKEN="test-internal-token")
    def test_stock_check_requires_internal_service_token(self):
        category = Category.objects.create(name="Electronics", description="Devices")
        product = Product.objects.create(
            category=category,
            name="USB-C Hub",
            description="Adapter",
            price="59.99",
            stock=20,
            sku="USBHUB-001",
            is_active=True,
        )

        unauthorized_response = self.client.post(
            "/products/stock/check/",
            {"products": [{"product_id": product.id, "quantity": 2}]},
            format="json",
        )
        self.assertEqual(unauthorized_response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertFalse(unauthorized_response.data["success"])

        authorized_response = self.client.post(
            "/products/stock/check/",
            {"products": [{"product_id": product.id, "quantity": 2}]},
            format="json",
            HTTP_X_SERVICE_TOKEN="test-internal-token",
        )
        self.assertEqual(authorized_response.status_code, status.HTTP_200_OK)
        self.assertTrue(authorized_response.data["success"])
        self.assertTrue(authorized_response.data["data"]["available"])
