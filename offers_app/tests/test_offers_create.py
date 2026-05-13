from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token
from offers_app.models import Offer
from profiles_app.models import UserProfile


class OffersCreateAPITest(APITestCase):

    def setUp(self):
        self.url = reverse("offers-list")
        self.business_user = User.objects.create_user(
            username="business_user",
            email="business@mail.de",
            password="securePassword123",
        )
        UserProfile.objects.create(user=self.business_user, type="business")
        self.token = Token.objects.create(user=self.business_user)
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token.key)

        self.customer_user = User.objects.create_user(
            username="customer_user",
            email="customer@mail.de",
            password="securePassword123",
        )
        UserProfile.objects.create(user=self.customer_user, type="customer")
        self.customer_token = Token.objects.create(user=self.customer_user)

        self.valid_payload = {
            "title": "Grafikdesign-Paket",
            "image": None,
            "description": "Ein umfassendes Grafikdesign-Paket.",
            "details": [
                {
                    "title": "Basic Design", "revisions": 2,
                    "delivery_time_in_days": 5, "price": 100,
                    "features": ["Logo Design", "Visitenkarte"], "offer_type": "basic",
                },
                {
                    "title": "Standard Design", "revisions": 5,
                    "delivery_time_in_days": 7, "price": 200,
                    "features": ["Logo Design", "Visitenkarte", "Briefpapier"], "offer_type": "standard",
                },
                {
                    "title": "Premium Design", "revisions": 10,
                    "delivery_time_in_days": 10, "price": 500,
                    "features": ["Logo Design", "Visitenkarte", "Briefpapier", "Flyer"], "offer_type": "premium",
                },
            ],
        }

    # --- 201 Happy Path ---

    def test_offers_create_returns_201(self):
        response = self.client.post(self.url, self.valid_payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_offers_create_returns_correct_fields(self):
        response = self.client.post(self.url, self.valid_payload, format="json")
        self.assertIn("id", response.data)
        self.assertIn("title", response.data)
        self.assertIn("description", response.data)
        self.assertIn("details", response.data)

    def test_offers_create_returns_3_details(self):
        response = self.client.post(self.url, self.valid_payload, format="json")
        self.assertEqual(len(response.data["details"]), 3)

    def test_offers_create_details_have_ids(self):
        response = self.client.post(self.url, self.valid_payload, format="json")
        for detail in response.data["details"]:
            self.assertIn("id", detail)

    def test_offers_create_persists_to_db(self):
        self.client.post(self.url, self.valid_payload, format="json")
        self.assertEqual(Offer.objects.count(), 1)

    # --- 400 Bad Request ---

    def test_offers_create_fails_if_less_than_3_details(self):
        payload = {**self.valid_payload, "details": self.valid_payload["details"][:2]}
        response = self.client.post(self.url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_offers_create_fails_if_details_missing(self):
        payload = {k: v for k, v in self.valid_payload.items() if k != "details"}
        response = self.client.post(self.url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_offers_create_fails_if_title_missing(self):
        payload = {k: v for k, v in self.valid_payload.items() if k != "title"}
        response = self.client.post(self.url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # --- 401 Not authenticated ---

    def test_offers_create_returns_401_if_not_authenticated(self):
        self.client.credentials()
        response = self.client.post(self.url, self.valid_payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # --- 403 Forbidden ---

    def test_offers_create_returns_403_if_customer(self):
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.customer_token.key)
        response = self.client.post(self.url, self.valid_payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)