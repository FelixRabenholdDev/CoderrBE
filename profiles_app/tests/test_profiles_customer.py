from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token
from profiles_app.models import UserProfile

class CustomerProfilesAPITest(APITestCase):

    def setUp(self):
        self.url = reverse("profiles-customer")
        self.user = User.objects.create_user(
            username="auth_user",
            email="auth@mail.de",
            password="securePassword123",
        )
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token.key)

        self.customer_user_1 = User.objects.create_user(
            username="customer_jane",
            email="jane@mail.de",
            password="securePassword123",
            first_name="Jane",
            last_name="Doe",
        )
        self.customer_profile_1 = UserProfile.objects.create(
            user=self.customer_user_1,
            type="customer",
        )

        self.customer_user_2 = User.objects.create_user(
            username="customer_john",
            email="john@mail.de",
            password="securePassword123",
            first_name="John",
            last_name="Smith",
        )
        self.customer_profile_2 = UserProfile.objects.create(
            user=self.customer_user_2,
            type="customer",
        )

        self.business_user = User.objects.create_user(
            username="business_user",
            email="business@mail.de",
            password="securePassword123",
        )
        UserProfile.objects.create(user=self.business_user, type="business")

    # --- 200 Happy Path ---

    def test_customer_profiles_returns_200(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_customer_profiles_returns_list(self):
        response = self.client.get(self.url)
        self.assertIsInstance(response.data, list)

    def test_customer_profiles_returns_only_customer_users(self):
        response = self.client.get(self.url)
        for profile in response.data:
            self.assertEqual(profile["type"], "customer")

    def test_customer_profiles_returns_correct_count(self):
        response = self.client.get(self.url)
        self.assertEqual(len(response.data), 2)

    def test_customer_profiles_returns_correct_fields(self):
        response = self.client.get(self.url)
        expected_fields = [
            "user", "username", "first_name", "last_name",
            "file", "uploaded_at", "type",
        ]
        for field in expected_fields:
            self.assertIn(field, response.data[0])

    def test_customer_profiles_string_fields_are_never_null(self):
        empty_user = User.objects.create_user(username="empty_customer", password="pass123")
        UserProfile.objects.create(user=empty_user, type="customer")
        response = self.client.get(self.url)
        empty_profile = next(p for p in response.data if p["username"] == "empty_customer")
        for field in ["first_name", "last_name"]:
            self.assertEqual(empty_profile[field], "", f"{field} should be '' not None")

    # --- 401 Not authenticated ---

    def test_customer_profiles_returns_401_if_not_authenticated(self):
        self.client.credentials()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)