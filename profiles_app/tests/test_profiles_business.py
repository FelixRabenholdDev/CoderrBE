from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token
from profiles_app.models import UserProfile


class BusinessProfilesAPITest(APITestCase):

    def setUp(self):
        self.url = reverse("profiles-business")
        self.user = User.objects.create_user(
            username="auth_user",
            email="auth@mail.de",
            password="securePassword123",
        )
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token.key)

        self.business_user_1 = User.objects.create_user(
            username="max_business",
            email="max@business.de",
            password="securePassword123",
            first_name="Max",
            last_name="Mustermann",
        )
        self.business_profile_1 = UserProfile.objects.create(
            user=self.business_user_1,
            type="business",
            location="Berlin",
            tel="123456789",
            description="Business description",
            working_hours="9-17",
        )

        self.business_user_2 = User.objects.create_user(
            username="anna_business",
            email="anna@business.de",
            password="securePassword123",
            first_name="Anna",
            last_name="Schmidt",
        )
        self.business_profile_2 = UserProfile.objects.create(
            user=self.business_user_2,
            type="business",
            location="Hamburg",
            tel="987654321",
            description="Another business",
            working_hours="8-16",
        )

        self.customer_user = User.objects.create_user(
            username="customer_user",
            email="customer@mail.de",
            password="securePassword123",
        )
        UserProfile.objects.create(user=self.customer_user, type="customer")

    # --- 200 Happy Path ---

    def test_business_profiles_returns_200(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_business_profiles_returns_list(self):
        response = self.client.get(self.url)
        self.assertIsInstance(response.data, list)

    def test_business_profiles_returns_only_business_users(self):
        response = self.client.get(self.url)
        for profile in response.data:
            self.assertEqual(profile["type"], "business")

    def test_business_profiles_returns_correct_count(self):
        response = self.client.get(self.url)
        self.assertEqual(len(response.data), 2)

    def test_business_profiles_returns_correct_fields(self):
        response = self.client.get(self.url)
        expected_fields = [
            "user", "username", "first_name", "last_name",
            "file", "location", "tel", "description", "working_hours", "type",
        ]
        for field in expected_fields:
            self.assertIn(field, response.data[0])

    def test_business_profiles_string_fields_are_never_null(self):
        empty_user = User.objects.create_user(username="empty_biz", password="pass123")
        UserProfile.objects.create(user=empty_user, type="business")
        response = self.client.get(self.url)
        empty_profile = next(p for p in response.data if p["username"] == "empty_biz")
        for field in ["first_name", "last_name", "location", "tel", "description", "working_hours"]:
            self.assertEqual(empty_profile[field], "", f"{field} should be '' not None")

    # --- 401 Not authenticated ---

    def test_business_profiles_returns_401_if_not_authenticated(self):
        self.client.credentials()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)