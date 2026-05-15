from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token
from orders_app.models import Order
from profiles_app.models import UserProfile


class OrdersPatchAPITest(APITestCase):

    def setUp(self):
        self.customer_user = User.objects.create_user(
            username="customer_user",
            email="customer@mail.de",
            password="securePassword123",
        )
        UserProfile.objects.create(user=self.customer_user, type="customer")
        self.customer_token = Token.objects.create(user=self.customer_user)

        self.business_user = User.objects.create_user(
            username="business_user",
            email="business@mail.de",
            password="securePassword123",
        )
        UserProfile.objects.create(user=self.business_user, type="business")
        self.business_token = Token.objects.create(user=self.business_user)

        self.other_business_user = User.objects.create_user(
            username="other_business",
            email="other@mail.de",
            password="securePassword123",
        )
        UserProfile.objects.create(user=self.other_business_user, type="business")
        self.other_business_token = Token.objects.create(user=self.other_business_user)

        self.order = Order.objects.create(
            customer_user=self.customer_user,
            business_user=self.business_user,
            title="Logo Design",
            revisions=3,
            delivery_time_in_days=5,
            price=150,
            features=["Logo Design"],
            offer_type="basic",
            status="in_progress",
        )
        self.url = reverse("order-detail", kwargs={"pk": self.order.pk})

    # --- 200 Happy Path ---

    def test_orders_patch_returns_200(self):
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.business_token.key)
        response = self.client.patch(self.url, {"status": "completed"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_orders_patch_updates_status(self):
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.business_token.key)
        response = self.client.patch(self.url, {"status": "completed"}, format="json")
        self.assertEqual(response.data["status"], "completed")

    def test_orders_patch_returns_correct_fields(self):
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.business_token.key)
        response = self.client.patch(self.url, {"status": "completed"}, format="json")
        expected_fields = [
            "id", "customer_user", "business_user", "title", "revisions",
            "delivery_time_in_days", "price", "features", "offer_type",
            "status", "created_at", "updated_at",
        ]
        for field in expected_fields:
            self.assertIn(field, response.data)

    def test_orders_patch_status_cancelled(self):
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.business_token.key)
        response = self.client.patch(self.url, {"status": "cancelled"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], "cancelled")

    # --- 400 Bad Request ---

    def test_orders_patch_fails_if_status_invalid(self):
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.business_token.key)
        response = self.client.patch(self.url, {"status": "invalid_status"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # --- 401 Not authenticated ---

    def test_orders_patch_returns_401_if_not_authenticated(self):
        response = self.client.patch(self.url, {"status": "completed"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # --- 403 Not business user ---

    def test_orders_patch_returns_403_if_customer(self):
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.customer_token.key)
        response = self.client.patch(self.url, {"status": "completed"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_orders_patch_returns_403_if_not_assigned_business_user(self):
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.other_business_token.key)
        response = self.client.patch(self.url, {"status": "completed"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # --- 404 Not found ---

    def test_orders_patch_returns_404_if_not_found(self):
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.business_token.key)
        url = reverse("order-detail", kwargs={"pk": 99999})
        response = self.client.patch(url, {"status": "completed"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)