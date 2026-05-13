from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token
from offers_app.models import Offer, OfferDetail
from profiles_app.models import UserProfile


class OfferDeleteAPITest(APITestCase):

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
        OfferDetail.objects.create(
            offer=self.offer, title="Basic", revisions=2,
            delivery_time_in_days=5, price=100,
            features=["Logo Design"], offer_type="basic",
        )
        self.url = reverse("offer-detail", kwargs={"pk": self.offer.pk})

    # --- 204 Happy Path ---

    def test_offer_delete_returns_204(self):
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_offer_delete_removes_from_db(self):
        self.client.delete(self.url)
        self.assertEqual(Offer.objects.count(), 0)

    def test_offer_delete_returns_no_content(self):
        response = self.client.delete(self.url)
        self.assertEqual(len(response.content), 0)

    # --- 401 Not authenticated ---

    def test_offer_delete_returns_401_if_not_authenticated(self):
        self.client.credentials()
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # --- 403 Forbidden ---

    def test_offer_delete_returns_403_if_not_owner(self):
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.other_token.key)
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # --- 404 Not found ---

    def test_offer_delete_returns_404_if_not_found(self):
        url = reverse("offer-detail", kwargs={"pk": 99999})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)