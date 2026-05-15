from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token
from orders_app.models import Order
from profiles_app.models import UserProfile


class OrderCountAPITest(APITestCase):

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

        self.url_order_count = reverse("order-count", kwargs={"business_user_id": self.business_user.id})
        self.url_completed_count = reverse("completed-order-count", kwargs={"business_user_id": self.business_user.id})

        Order.objects.create(
            customer_user=self.customer_user, business_user=self.business_user,
            title="Order 1", revisions=2, delivery_time_in_days=5,
            price=100, features=[], offer_type="basic", status="in_progress",
        )
        Order.objects.create(
            customer_user=self.customer_user, business_user=self.business_user,
            title="Order 2", revisions=2, delivery_time_in_days=5,
            price=100, features=[], offer_type="basic", status="in_progress",
        )
        Order.objects.create(
            customer_user=self.customer_user, business_user=self.business_user,
            title="Order 3", revisions=2, delivery_time_in_days=5,
            price=100, features=[], offer_type="basic", status="completed",
        )
        Order.objects.create(
            customer_user=self.customer_user, business_user=self.business_user,
            title="Order 4", revisions=2, delivery_time_in_days=5,
            price=100, features=[], offer_type="basic", status="completed",
        )
        Order.objects.create(
            customer_user=self.customer_user, business_user=self.business_user,
            title="Order 5", revisions=2, delivery_time_in_days=5,
            price=100, features=[], offer_type="basic", status="cancelled",
        )

    # --- order-count ---

    def test_order_count_returns_200(self):
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.customer_token.key)
        response = self.client.get(self.url_order_count)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_order_count_returns_correct_count(self):
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.customer_token.key)
        response = self.client.get(self.url_order_count)
        self.assertIn("order_count", response.data)
        self.assertEqual(response.data["order_count"], 2)

    def test_order_count_returns_401_if_not_authenticated(self):
        response = self.client.get(self.url_order_count)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_order_count_returns_404_if_business_user_not_found(self):
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.customer_token.key)
        url = reverse("order-count", kwargs={"business_user_id": 99999})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # --- completed-order-count ---

    def test_completed_order_count_returns_200(self):
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.customer_token.key)
        response = self.client.get(self.url_completed_count)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_completed_order_count_returns_correct_count(self):
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.customer_token.key)
        response = self.client.get(self.url_completed_count)
        self.assertIn("completed_order_count", response.data)
        self.assertEqual(response.data["completed_order_count"], 2)

    def test_completed_order_count_returns_401_if_not_authenticated(self):
        response = self.client.get(self.url_completed_count)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_completed_order_count_returns_404_if_business_user_not_found(self):
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.customer_token.key)
        url = reverse("completed-order-count", kwargs={"business_user_id": 99999})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)