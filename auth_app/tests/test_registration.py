from django.urls import reverse
from django.contrib.auth.models import User

from rest_framework import status
from rest_framework.test import APITestCase

from auth_app.models import UserProfile


class RegistrationAPITest(APITestCase):

    def setUp(self):
        self.url = reverse("registration")
        self.valid_payload = {
            "username": "testuser",
            "email": "test@mail.de",
            "password": "securePassword123",
            "repeated_password": "securePassword123",
            "type": "customer",
        }
    
#---Happy Path 201---

    def test_registration_returns_201_on_success(self):
        response = self.client.post(self.url, self.valid_payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    def test_registration_returns_token(self):
        response = self.client.post(self.url, self.valid_payload, format="json")
        self.assertIn("token", response.data)
        self.assertTrue(len(response.data["token"]) > 0)

    def test_registration_returns_correct_user_fields(self):
        response = self.client.post(self.url, self.valid_payload, format="json")
        self.assertIn("username", response.data)
        self.assertIn("email", response.data)
        self.assertIn("user_id", response.data)
        self.assertEqual(response.data["username"], self.valid_payload["username"])
        self.assertEqual(response.data["email"], self.valid_payload["email"])

    def test_registration_user_type_business(self):
        payload = {**self.valid_payload, "username": "bizuser", "email": "biz@mail.de", "type": "business"}
        response = self.client.post(self.url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_registration_creates_profile_with_correct_type_customer(self):
        self.client.post(self.url, self.valid_payload, format="json")
        user = User.objects.get(username="testuser")
        self.assertEqual(user.profile.type, "customer")

    def test_registration_creates_profile_with_correct_type_business(self):
        payload = {**self.valid_payload, "username": "bizuser", "email": "biz@mail.de", "type": "business"}
        self.client.post(self.url, payload, format="json")
        user = User.objects.get(username="bizuser")
        self.assertEqual(user.profile.type, "business")

#---Unhappy Path 400---

    def test_registration_fails_if_passwords_dont_match(self):
        payload = {**self.valid_payload, "repeated_password": "wrongPassword"}
        response = self.client.post(self.url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_registration_fails_if_username_missing(self):
        payload = {k: v for k, v in self.valid_payload.items() if k != "username"}
        response = self.client.post(self.url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_registration_fails_if_email_missing(self):
        payload = {k: v for k, v in self.valid_payload.items() if k != "email"}
        response = self.client.post(self.url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_registration_fails_if_email_invalid(self):
        payload = {**self.valid_payload, "email": "not-an-email"}
        response = self.client.post(self.url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_registration_fails_if_username_already_exists(self):
        self.client.post(self.url, self.valid_payload, format="json")
        payload = {**self.valid_payload, "email": "other@mail.de"}
        response = self.client.post(self.url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_registration_fails_if_type_invalid(self):
        payload = {**self.valid_payload, "type": "admin"}
        response = self.client.post(self.url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)