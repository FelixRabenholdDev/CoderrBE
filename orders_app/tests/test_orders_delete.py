from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token
from orders_app.models import Order
from profiles_app.models import UserProfile


class OrdersDeleteAPITest(APITestCase):

    def setUp(self):
        self.admin_user = User.objects.create_user(
            username="admin_user",
            email="admin@mail.de",
            password="securePassword123",
            is_staff=True,
        )
        self.admin_token = Token.objects.create(user=self.admin_user)

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

    # --- 204 Happy Path ---

    def test_orders_delete_returns_204(self):
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.admin_token.key)
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_orders_delete_removes_from_db(self):
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.admin_token.key)
        self.client.delete(self.url)
        self.assertEqual(Order.objects.count(), 0)

    def test_orders_delete_returns_no_content(self):
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.admin_token.key)
        response = self.client.delete(self.url)
        self.assertEqual(len(response.content), 0)

    # --- 401 Not authenticated ---

    def test_orders_delete_returns_401_if_not_authenticated(self):
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # --- 403 Not admin ---

    def test_orders_delete_returns_403_if_customer(self):
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.customer_token.key)
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_orders_delete_returns_403_if_business(self):
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.business_token.key)
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # --- 404 Not found ---

    def test_orders_delete_returns_404_if_not_found(self):
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.admin_token.key)
        url = reverse("order-detail", kwargs={"pk": 99999})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)