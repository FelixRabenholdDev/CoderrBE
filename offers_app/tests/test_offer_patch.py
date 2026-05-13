from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token
from offers_app.models import Offer, OfferDetail
from profiles_app.models import UserProfile


class OfferPatchAPITest(APITestCase):

    def setUp(self):
        self.business_user = User.objects.create_user(
            username="business_user",
            email="business@mail.de",
            password="securePassword123",
        )
        UserProfile.objects.create(user=self.business_user, type="business")
        self.token = Token.objects.create(user=self.business_user)
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token.key)

        self.other_user = User.objects.create_user(
            username="other_user",
            email="other@mail.de",
            password="securePassword123",
        )
        UserProfile.objects.create(user=self.other_user, type="business")
        self.other_token = Token.objects.create(user=self.other_user)

        self.offer = Offer.objects.create(
            user=self.business_user,
            title="Grafikdesign-Paket",
            description="Ein umfassendes Grafikdesign-Paket.",
        )
        self.detail_basic = OfferDetail.objects.create(
            offer=self.offer, title="Basic", revisions=2,
            delivery_time_in_days=5, price=100,
            features=["Logo Design"], offer_type="basic",
        )
        self.detail_standard = OfferDetail.objects.create(
            offer=self.offer, title="Standard", revisions=5,
            delivery_time_in_days=10, price=200,
            features=["Logo Design", "Visitenkarte"], offer_type="standard",
        )
        self.detail_premium = OfferDetail.objects.create(
            offer=self.offer, title="Premium", revisions=10,
            delivery_time_in_days=14, price=500,
            features=["Logo Design", "Visitenkarte", "Flyer"], offer_type="premium",
        )
        self.url = reverse("offer-detail", kwargs={"pk": self.offer.pk})

    # --- 200 Happy Path ---

    def test_offer_patch_returns_200(self):
        response = self.client.patch(self.url, {"title": "Updated Title"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_offer_patch_updates_title(self):
        response = self.client.patch(self.url, {"title": "Updated Title"}, format="json")
        self.assertEqual(response.data["title"], "Updated Title")

    def test_offer_patch_updates_detail_by_offer_type(self):
        payload = {
            "details": [
                {
                    "title": "Basic Design Updated", "revisions": 3,
                    "delivery_time_in_days": 6, "price": 120,
                    "features": ["Logo Design", "Flyer"], "offer_type": "basic",
                }
            ]
        }
        response = self.client.patch(self.url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        basic = next(d for d in response.data["details"] if d["offer_type"] == "basic")
        self.assertEqual(basic["title"], "Basic Design Updated")
        self.assertEqual(basic["revisions"], 3)

    def test_offer_patch_unspecified_details_remain_unchanged(self):
        payload = {
            "details": [
                {
                    "title": "Basic Updated", "revisions": 3,
                    "delivery_time_in_days": 6, "price": 120,
                    "features": ["Logo"], "offer_type": "basic",
                }
            ]
        }
        response = self.client.patch(self.url, payload, format="json")
        standard = next(d for d in response.data["details"] if d["offer_type"] == "standard")
        self.assertEqual(standard["title"], "Standard")

    def test_offer_patch_returns_all_fields(self):
        response = self.client.patch(self.url, {"title": "Updated"}, format="json")
        expected_fields = ["id", "title", "image", "description", "details"]
        for field in expected_fields:
            self.assertIn(field, response.data)

    # --- 401 Not authenticated ---

    def test_offer_patch_returns_401_if_not_authenticated(self):
        self.client.credentials()
        response = self.client.patch(self.url, {"title": "Updated"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # --- 403 Forbidden ---

    def test_offer_patch_returns_403_if_not_owner(self):
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.other_token.key)
        response = self.client.patch(self.url, {"title": "Updated"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # --- 404 Not found ---

    def test_offer_patch_returns_404_if_not_found(self):
        url = reverse("offer-detail", kwargs={"pk": 99999})
        response = self.client.patch(url, {"title": "Updated"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)