from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token
from orders_app.models import Order
from profiles_app.models import UserProfile


class OrdersListAPITest(APITestCase):

    def setUp(self):
        self.url = reverse("orders-list")

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

        self.other_user = User.objects.create_user(
            username="other_user",
            email="other@mail.de",
            password="securePassword123",
        )
        UserProfile.objects.create(user=self.other_user, type="customer")
        self.other_token = Token.objects.create(user=self.other_user)

        self.order = Order.objects.create(
            customer_user=self.customer_user,
            business_user=self.business_user,
            title="Logo Design",
            revisions=3,
            delivery_time_in_days=5,
            price=150,
            features=["Logo Design", "Visitenkarten"],
            offer_type="basic",
            status="in_progress",
        )

    # --- 200 Happy Path ---

    def test_orders_list_returns_200_for_customer(self):
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.customer_token.key)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_orders_list_returns_200_for_business(self):
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.business_token.key)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_orders_list_returns_correct_fields(self):
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.customer_token.key)
        response = self.client.get(self.url)
        expected_fields = [
            "id", "customer_user", "business_user", "title", "revisions",
            "delivery_time_in_days", "price", "features", "offer_type",
            "status", "created_at", "updated_at",
        ]
        for field in expected_fields:
            self.assertIn(field, response.data[0])

    def test_orders_list_returns_only_own_orders_as_customer(self):
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.customer_token.key)
        response = self.client.get(self.url)
        for order in response.data:
            self.assertEqual(order["customer_user"], self.customer_user.id)

    def test_orders_list_returns_only_own_orders_as_business(self):
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.business_token.key)
        response = self.client.get(self.url)
        for order in response.data:
            self.assertEqual(order["business_user"], self.business_user.id)

    def test_orders_list_returns_empty_for_unrelated_user(self):
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.other_token.key)
        response = self.client.get(self.url)
        self.assertEqual(response.data, [])

    # --- 401 Not authenticated ---

    def test_orders_list_returns_401_if_not_authenticated(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)