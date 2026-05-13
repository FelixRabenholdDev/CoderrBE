from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token
from profiles_app.models import UserProfile


class ProfilePatchAPITest(APITestCase):

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

        self.valid_payload = {
            "first_name": "Max",
            "last_name": "Mustermann",
            "location": "Berlin",
            "tel": "987654321",
            "description": "Updated business description",
            "working_hours": "10-18",
            "email": "new_email@business.de",
        }

    # --- 200 Happy Path ---

    def test_profile_patch_returns_200(self):
        response = self.client.patch(self.url, self.valid_payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_profile_patch_updates_profile_fields(self):
        response = self.client.patch(self.url, self.valid_payload, format="json")
        self.assertEqual(response.data["location"], "Berlin")
        self.assertEqual(response.data["tel"], "987654321")
        self.assertEqual(response.data["description"], "Updated business description")
        self.assertEqual(response.data["working_hours"], "10-18")

    def test_profile_patch_updates_email(self):
        response = self.client.patch(self.url, self.valid_payload, format="json")
        self.assertEqual(response.data["email"], "new_email@business.de")
        self.user.refresh_from_db()
        self.assertEqual(self.user.email, "new_email@business.de")

    def test_profile_patch_updates_first_and_last_name(self):
        payload = {**self.valid_payload, "first_name": "Hans", "last_name": "Müller"}
        response = self.client.patch(self.url, payload, format="json")
        self.assertEqual(response.data["first_name"], "Hans")
        self.assertEqual(response.data["last_name"], "Müller")
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, "Hans")
        self.assertEqual(self.user.last_name, "Müller")

    def test_profile_patch_partial_update(self):
        response = self.client.patch(self.url, {"tel": "000111222"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["tel"], "000111222")

    def test_profile_patch_string_fields_are_never_null(self):
        response = self.client.patch(self.url, {}, format="json")
        for field in ["first_name", "last_name", "location", "tel", "description", "working_hours"]:
            self.assertNotEqual(response.data[field], None, f"{field} sollte nicht None sein")

    # --- 401 Not authenticated ---

    def test_profile_patch_returns_401_if_not_authenticated(self):
        self.client.credentials()
        response = self.client.patch(self.url, self.valid_payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # --- 403 Forbidden ---

    def test_profile_patch_returns_403_if_not_owner(self):
        other_user = User.objects.create_user(
            username="other_user",
            email="other@mail.de",
            password="securePassword123",
        )
        UserProfile.objects.create(user=other_user, type="customer")
        other_token = Token.objects.create(user=other_user)
        self.client.credentials(HTTP_AUTHORIZATION="Token " + other_token.key)
        response = self.client.patch(self.url, self.valid_payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # --- 404 Not found ---

    def test_profile_patch_returns_404_if_not_found(self):
        url = reverse("profile-detail", kwargs={"pk": 99999})
        response = self.client.patch(self.url, self.valid_payload, format="json")
        self.assertNotEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        response = self.client.patch(url, self.valid_payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)