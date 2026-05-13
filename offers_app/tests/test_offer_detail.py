from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token
from offers_app.models import Offer, OfferDetail
from profiles_app.models import UserProfile


class OfferDetailAPITest(APITestCase):

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
        OfferDetail.objects.create(
            offer=self.offer, title="Basic", revisions=2,
            delivery_time_in_days=5, price=50,
            features=["Logo Design"], offer_type="basic",
        )
        OfferDetail.objects.create(
            offer=self.offer, title="Standard", revisions=5,
            delivery_time_in_days=7, price=100,
            features=["Logo Design", "Visitenkarte"], offer_type="standard",
        )
        OfferDetail.objects.create(
            offer=self.offer, title="Premium", revisions=10,
            delivery_time_in_days=10, price=200,
            features=["Logo Design", "Visitenkarte", "Flyer"], offer_type="premium",
        )
        self.url = reverse("offer-detail", kwargs={"pk": self.offer.pk})

    # --- 200 Happy Path ---

    def test_offer_detail_returns_200(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_offer_detail_returns_correct_fields(self):
        response = self.client.get(self.url)
        expected_fields = [
            "id", "user", "title", "image", "description",
            "created_at", "updated_at", "details", "min_price", "min_delivery_time",
        ]
        for field in expected_fields:
            self.assertIn(field, response.data)

    def test_offer_detail_details_contain_id_and_url(self):
        response = self.client.get(self.url)
        for detail in response.data["details"]:
            self.assertIn("id", detail)
            self.assertIn("url", detail)

    def test_offer_detail_min_price_is_correct(self):
        response = self.client.get(self.url)
        self.assertEqual(float(response.data["min_price"]), 50.0)

    def test_offer_detail_min_delivery_time_is_correct(self):
        response = self.client.get(self.url)
        self.assertEqual(response.data["min_delivery_time"], 5)

    # --- 401 Not authenticated ---

    def test_offer_detail_returns_401_if_not_authenticated(self):
        self.client.credentials()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # --- 404 Not found ---

    def test_offer_detail_returns_404_if_not_found(self):
        url = reverse("offer-detail", kwargs={"pk": 99999})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)