from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token
from profiles_app.models import UserProfile


class ProfileDetailAPITest(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="max_mustermann",
            email="max@business.de",
            password="securePassword123",
            first_name="Max",
            last_name="Mustermann",
        )
        self.profile = UserProfile.objects.create(
            user=self.user,
            type="business",
            location="Berlin",
            tel="123456789",
            description="Business description",
            working_hours="9-17",
        )
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token.key)
        self.url = reverse("profile-detail", kwargs={"pk": self.user.pk})

    # --- 200 Happy Path ---

    def test_profile_detail_returns_200(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_profile_detail_returns_correct_fields(self):
        response = self.client.get(self.url)
        self.assertEqual(response.data["user"], self.user.id)
        self.assertEqual(response.data["username"], "max_mustermann")
        self.assertEqual(response.data["first_name"], "Max")
        self.assertEqual(response.data["last_name"], "Mustermann")
        self.assertEqual(response.data["location"], "Berlin")
        self.assertEqual(response.data["tel"], "123456789")
        self.assertEqual(response.data["description"], "Business description")
        self.assertEqual(response.data["working_hours"], "9-17")
        self.assertEqual(response.data["type"], "business")
        self.assertEqual(response.data["email"], "max@business.de")
        self.assertIn("created_at", response.data)
        self.assertIn("file", response.data)

    def test_profile_detail_string_fields_are_never_null(self):
        profile = UserProfile.objects.create(
            user=User.objects.create_user(username="emptyuser", password="pass123"),
            type="customer",
        )
        token = Token.objects.create(user=profile.user)
        self.client.credentials(HTTP_AUTHORIZATION="Token " + token.key)
        url = reverse("profile-detail", kwargs={"pk": profile.user.pk})
        response = self.client.get(url)
        for field in ["first_name", "last_name", "location", "tel", "description", "working_hours"]:
            self.assertEqual(response.data[field], "", f"{field} sollte '' sein, nicht None")

    # --- 401 Not authenticated ---

    def test_profile_detail_returns_401_if_not_authenticated(self):
        self.client.credentials()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # --- 404 Not found ---

    def test_profile_detail_returns_404_if_not_found(self):
        url = reverse("profile-detail", kwargs={"pk": 99999})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)