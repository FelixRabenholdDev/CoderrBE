from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token
from offers_app.models import Offer, OfferDetail
from profiles_app.models import UserProfile


class OffersListAPITest(APITestCase):

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

        self.offer = Offer.objects.create(
            user=self.business_user,
            title="Website Design",
            description="Professionelles Website-Design...",
        )
        OfferDetail.objects.create(
            offer=self.offer, title="Basic", revisions=2,
            delivery_time_in_days=7, price=100,
            features=["Logo Design"], offer_type="basic",
        )
        OfferDetail.objects.create(
            offer=self.offer, title="Standard", revisions=5,
            delivery_time_in_days=10, price=200,
            features=["Logo Design", "Visitenkarte"], offer_type="standard",
        )
        OfferDetail.objects.create(
            offer=self.offer, title="Premium", revisions=10,
            delivery_time_in_days=14, price=500,
            features=["Logo Design", "Visitenkarte", "Flyer"], offer_type="premium",
        )

    # --- 200 Happy Path ---

    def test_offers_list_returns_200(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_offers_list_is_paginated(self):
        response = self.client.get(self.url)
        self.assertIn("count", response.data)
        self.assertIn("results", response.data)
        self.assertIn("next", response.data)
        self.assertIn("previous", response.data)

    def test_offers_list_returns_correct_fields(self):
        response = self.client.get(self.url)
        result = response.data["results"][0]
        expected_fields = [
            "id", "user", "title", "image", "description",
            "created_at", "updated_at", "details", "min_price",
            "min_delivery_time", "user_details",
        ]
        for field in expected_fields:
            self.assertIn(field, result)

    def test_offers_list_details_contain_id_and_url(self):
        response = self.client.get(self.url)
        result = response.data["results"][0]
        for detail in result["details"]:
            self.assertIn("id", detail)
            self.assertIn("url", detail)

    def test_offers_list_user_details_contain_correct_fields(self):
        response = self.client.get(self.url)
        user_details = response.data["results"][0]["user_details"]
        self.assertIn("first_name", user_details)
        self.assertIn("last_name", user_details)
        self.assertIn("username", user_details)

    def test_offers_list_min_price_is_correct(self):
        response = self.client.get(self.url)
        result = response.data["results"][0]
        self.assertEqual(float(result["min_price"]), 100.0)

    def test_offers_list_min_delivery_time_is_correct(self):
        response = self.client.get(self.url)
        result = response.data["results"][0]
        self.assertEqual(result["min_delivery_time"], 7)

    # --- Filtering ---

    def test_offers_list_filter_by_creator_id(self):
        response = self.client.get(self.url, {"creator_id": self.business_user.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for result in response.data["results"]:
            self.assertEqual(result["user"], self.business_user.id)

    def test_offers_list_filter_by_min_price(self):
        response = self.client.get(self.url, {"min_price": 150})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for result in response.data["results"]:
            self.assertGreaterEqual(float(result["min_price"]), 150)

    def test_offers_list_filter_by_max_delivery_time(self):
        response = self.client.get(self.url, {"max_delivery_time": 10})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for result in response.data["results"]:
            self.assertLessEqual(result["min_delivery_time"], 10)

    def test_offers_list_search_by_title(self):
        response = self.client.get(self.url, {"search": "Website"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(response.data["count"], 0)

    def test_offers_list_search_by_description(self):
        response = self.client.get(self.url, {"search": "Professionelles"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(response.data["count"], 0)

    def test_offers_list_ordering_by_updated_at(self):
        response = self.client.get(self.url, {"ordering": "updated_at"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_offers_list_ordering_by_min_price(self):
        response = self.client.get(self.url, {"ordering": "min_price"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_offers_list_no_auth_still_returns_200(self):
        self.client.credentials()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)