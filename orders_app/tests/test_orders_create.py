from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token
from offers_app.models import Offer, OfferDetail
from orders_app.models import Order
from profiles_app.models import UserProfile


class OrdersCreateAPITest(APITestCase):

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

        self.offer = Offer.objects.create(
            user=self.business_user,
            title="Grafikdesign-Paket",
            description="Ein umfassendes Grafikdesign-Paket.",
        )
        self.offer_detail = OfferDetail.objects.create(
            offer=self.offer,
            title="Logo Design",
            revisions=3,
            delivery_time_in_days=5,
            price=150,
            features=["Logo Design", "Visitenkarten"],
            offer_type="basic",
        )
        self.valid_payload = {"offer_detail_id": self.offer_detail.id}

    # --- 201 Happy Path ---

    def test_orders_create_returns_201(self):
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.customer_token.key)
        response = self.client.post(self.url, self.valid_payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_orders_create_returns_correct_fields(self):
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.customer_token.key)
        response = self.client.post(self.url, self.valid_payload, format="json")
        expected_fields = [
            "id", "customer_user", "business_user", "title", "revisions",
            "delivery_time_in_days", "price", "features", "offer_type",
            "status", "created_at", "updated_at",
        ]
        for field in expected_fields:
            self.assertIn(field, response.data)

    def test_orders_create_sets_correct_users(self):
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.customer_token.key)
        response = self.client.post(self.url, self.valid_payload, format="json")
        self.assertEqual(response.data["customer_user"], self.customer_user.id)
        self.assertEqual(response.data["business_user"], self.business_user.id)

    def test_orders_create_sets_status_in_progress(self):
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.customer_token.key)
        response = self.client.post(self.url, self.valid_payload, format="json")
        self.assertEqual(response.data["status"], "in_progress")

    def test_orders_create_copies_offer_detail_data(self):
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.customer_token.key)
        response = self.client.post(self.url, self.valid_payload, format="json")
        self.assertEqual(response.data["title"], self.offer_detail.title)
        self.assertEqual(response.data["revisions"], self.offer_detail.revisions)
        self.assertEqual(response.data["delivery_time_in_days"], self.offer_detail.delivery_time_in_days)
        self.assertEqual(float(response.data["price"]), float(self.offer_detail.price))
        self.assertEqual(response.data["offer_type"], self.offer_detail.offer_type)

    def test_orders_create_persists_to_db(self):
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.customer_token.key)
        self.client.post(self.url, self.valid_payload, format="json")
        self.assertEqual(Order.objects.count(), 1)

    # --- 400 Bad Request ---

    def test_orders_create_fails_if_offer_detail_id_missing(self):
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.customer_token.key)
        response = self.client.post(self.url, {}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # --- 401 Not authenticated ---

    def test_orders_create_returns_401_if_not_authenticated(self):
        response = self.client.post(self.url, self.valid_payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # --- 403 Not a customer ---

    def test_orders_create_returns_403_if_business_user(self):
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.business_token.key)
        response = self.client.post(self.url, self.valid_payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # --- 404 Not found ---

    def test_orders_create_returns_404_if_offer_detail_not_found(self):
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.customer_token.key)
        response = self.client.post(self.url, {"offer_detail_id": 99999}, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)