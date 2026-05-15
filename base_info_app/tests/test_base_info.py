from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase
from reviews_app.models import Review
from profiles_app.models import UserProfile
from offers_app.models import Offer, OfferDetail


class BaseInfoAPITest(APITestCase):

    def setUp(self):
        self.url = reverse("base-info")

        self.customer_user = User.objects.create_user(
            username="customer_user",
            email="customer@mail.de",
            password="securePassword123",
        )
        UserProfile.objects.create(user=self.customer_user, type="customer")

        self.business_user_1 = User.objects.create_user(
            username="business_user_1",
            email="business1@mail.de",
            password="securePassword123",
        )
        UserProfile.objects.create(user=self.business_user_1, type="business")

        self.business_user_2 = User.objects.create_user(
            username="business_user_2",
            email="business2@mail.de",
            password="securePassword123",
        )
        UserProfile.objects.create(user=self.business_user_2, type="business")

        Review.objects.create(
            business_user=self.business_user_1,
            reviewer=self.customer_user,
            rating=4,
            description="Sehr gut!",
        )
        Review.objects.create(
            business_user=self.business_user_2,
            reviewer=self.customer_user,
            rating=5,
            description="Top!",
        )

        offer = Offer.objects.create(
            user=self.business_user_1,
            title="Grafikdesign-Paket",
            description="Ein Paket.",
        )
        OfferDetail.objects.create(
            offer=offer, title="Basic", revisions=2,
            delivery_time_in_days=5, price=100,
            features=[], offer_type="basic",
        )
        OfferDetail.objects.create(
            offer=offer, title="Standard", revisions=5,
            delivery_time_in_days=7, price=200,
            features=[], offer_type="standard",
        )
        OfferDetail.objects.create(
            offer=offer, title="Premium", revisions=10,
            delivery_time_in_days=10, price=500,
            features=[], offer_type="premium",
        )

    # --- 200 Happy Path ---

    def test_base_info_returns_200(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_base_info_returns_correct_fields(self):
        response = self.client.get(self.url)
        expected_fields = [
            "review_count", "average_rating",
            "business_profile_count", "offer_count",
        ]
        for field in expected_fields:
            self.assertIn(field, response.data)

    def test_base_info_returns_correct_review_count(self):
        response = self.client.get(self.url)
        self.assertEqual(response.data["review_count"], 2)

    def test_base_info_returns_correct_average_rating(self):
        response = self.client.get(self.url)
        self.assertEqual(float(response.data["average_rating"]), 4.5)

    def test_base_info_average_rating_is_rounded_to_one_decimal(self):
        self.customer_user_2 = User.objects.create_user(
            username="customer_user_2",
            email="customer2@mail.de",
            password="securePassword123",
        )
        UserProfile.objects.create(user=self.customer_user_2, type="customer")
        business_user_3 = User.objects.create_user(
            username="business_user_3",
            email="business3@mail.de",
            password="securePassword123",
        )
        UserProfile.objects.create(user=business_user_3, type="business")
        Review.objects.create(
            business_user=business_user_3,
            reviewer=self.customer_user_2,
            rating=3,
            description="Ok.",
        )
        response = self.client.get(self.url)
        average = response.data["average_rating"]
        self.assertEqual(average, round(average, 1))

    def test_base_info_returns_correct_business_profile_count(self):
        response = self.client.get(self.url)
        self.assertEqual(response.data["business_profile_count"], 2)

    def test_base_info_returns_correct_offer_count(self):
        response = self.client.get(self.url)
        self.assertEqual(response.data["offer_count"], 1)

    def test_base_info_no_auth_required(self):
        self.client.credentials()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)