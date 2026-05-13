from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token
from offers_app.models import Offer, OfferDetail
from profiles_app.models import UserProfile


class OfferDetailItemAPITest(APITestCase):

    def setUp(self):
        self.business_user = User.objects.create_user(
            username="business_user",
            email="business@mail.de",
            password="securePassword123",
        )
        UserProfile.objects.create(user=self.business_user, type="business")
        self.token = Token.objects.create(user=self.business_user)
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token.key)

        self.offer = Offer.objects.create(
            user=self.business_user,
            title="Grafikdesign-Paket",
            description="Ein umfassendes Grafikdesign-Paket.",
        )
        self.offer_detail = OfferDetail.objects.create(
            offer=self.offer, title="Basic Design", revisions=2,
            delivery_time_in_days=5, price=100,
            features=["Logo Design", "Visitenkarte"], offer_type="basic",
        )
        self.url = reverse("offerdetail-detail", kwargs={"pk": self.offer_detail.pk})

    # --- 200 Happy Path ---

    def test_offerdetail_returns_200(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_offerdetail_returns_correct_fields(self):
        response = self.client.get(self.url)
        expected_fields = [
            "id", "title", "revisions", "delivery_time_in_days",
            "price", "features", "offer_type",
        ]
        for field in expected_fields:
            self.assertIn(field, response.data)

    def test_offerdetail_returns_correct_values(self):
        response = self.client.get(self.url)
        self.assertEqual(response.data["title"], "Basic Design")
        self.assertEqual(response.data["revisions"], 2)
        self.assertEqual(response.data["delivery_time_in_days"], 5)
        self.assertEqual(float(response.data["price"]), 100.0)
        self.assertEqual(response.data["features"], ["Logo Design", "Visitenkarte"])
        self.assertEqual(response.data["offer_type"], "basic")

    # --- 401 Not authenticated ---

    def test_offerdetail_returns_401_if_not_authenticated(self):
        self.client.credentials()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # --- 404 Not found ---

    def test_offerdetail_returns_404_if_not_found(self):
        url = reverse("offerdetail-detail", kwargs={"pk": 99999})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)