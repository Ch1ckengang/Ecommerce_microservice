from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

User = get_user_model()


class UserApiTests(APITestCase):
    def test_register_user_returns_success_envelope(self):
        response = self.client.post(
            "/users/register/",
            {
                "username": "alice",
                "email": "alice@example.com",
                "password": "strongpass123",
                "password_confirm": "strongpass123",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data["success"])
        self.assertEqual(response.data["data"]["username"], "alice")
        self.assertTrue(User.objects.filter(username="alice").exists())

    def test_token_issue_and_profile_flow(self):
        user = User.objects.create_user(
            username="bob",
            email="bob@example.com",
            password="strongpass123",
        )

        token_response = self.client.post(
            "/users/token/",
            {"username": "bob", "password": "strongpass123"},
            format="json",
        )

        self.assertEqual(token_response.status_code, status.HTTP_200_OK)
        access_token = token_response.data["data"]["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")

        profile_response = self.client.get("/users/me/")
        self.assertEqual(profile_response.status_code, status.HTTP_200_OK)
        self.assertEqual(profile_response.data["data"]["username"], user.username)

        update_response = self.client.put(
            "/users/me/",
            {
                "username": "bob",
                "email": "updated-bob@example.com",
                "first_name": "Bob",
                "last_name": "Builder",
            },
            format="json",
        )
        self.assertEqual(update_response.status_code, status.HTTP_200_OK)
        self.assertEqual(update_response.data["data"]["email"], "updated-bob@example.com")
