from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token


class LoginAPITest(APITestCase):

    def setUp(self):
        self.url = reverse("login")
        self.user = User.objects.create_user(
            username="testuser",
            email="test@mail.de",
            password="securePassword123",
        )
        self.valid_payload = {
            "username": "testuser",
            "password": "securePassword123",
        }

    #--- Happy Path 200---

    def test_login_returns_200_on_success(self):
        response = self.client.post(self.url, self.valid_payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_login_returns_token(self):
        response = self.client.post(self.url, self.valid_payload, format="json")
        self.assertIn("token", response.data)
        self.assertTrue(len(response.data["token"]) > 0)

    def test_login_returns_correct_user_fields(self):
        response = self.client.post(self.url, self.valid_payload, format="json")
        self.assertIn("username", response.data)
        self.assertIn("email", response.data)
        self.assertIn("user_id", response.data)
        self.assertEqual(response.data["username"], self.user.username)
        self.assertEqual(response.data["email"], self.user.email)
        self.assertEqual(response.data["user_id"], self.user.id)

    def test_login_returns_existing_token_if_already_exists(self):
        token = Token.objects.create(user=self.user)
        response = self.client.post(self.url, self.valid_payload, format="json")
        self.assertEqual(response.data["token"], token.key)

    # --- Validierungsfehler 400---

    def test_login_fails_if_password_wrong(self):
        payload = {**self.valid_payload, "password": "wrongPassword"}
        response = self.client.post(self.url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_fails_if_username_wrong(self):
        payload = {**self.valid_payload, "username": "wronguser"}
        response = self.client.post(self.url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_fails_if_username_missing(self):
        payload = {k: v for k, v in self.valid_payload.items() if k != "username"}
        response = self.client.post(self.url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_fails_if_password_missing(self):
        payload = {k: v for k, v in self.valid_payload.items() if k != "password"}
        response = self.client.post(self.url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)