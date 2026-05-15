from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token
from reviews_app.models import Review
from profiles_app.models import UserProfile


class ReviewsListAPITest(APITestCase):

    def setUp(self):
        self.url = reverse("reviews-list")

        self.customer_user = User.objects.create_user(
            username="customer_user",
            email="customer@mail.de",
            password="securePassword123",
        )
        UserProfile.objects.create(user=self.customer_user, type="customer")
        self.customer_token = Token.objects.create(user=self.customer_user)

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

        self.review_1 = Review.objects.create(
            business_user=self.business_user_1,
            reviewer=self.customer_user,
            rating=4,
            description="Sehr professioneller Service.",
        )
        self.review_2 = Review.objects.create(
            business_user=self.business_user_2,
            reviewer=self.customer_user,
            rating=5,
            description="Top Qualität und schnelle Lieferung!",
        )

    # --- 200 Happy Path ---

    def test_reviews_list_returns_200(self):
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.customer_token.key)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_reviews_list_returns_list(self):
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.customer_token.key)
        response = self.client.get(self.url)
        self.assertIsInstance(response.data, list)

    def test_reviews_list_returns_correct_count(self):
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.customer_token.key)
        response = self.client.get(self.url)
        self.assertEqual(len(response.data), 2)

    def test_reviews_list_returns_correct_fields(self):
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.customer_token.key)
        response = self.client.get(self.url)
        expected_fields = [
            "id", "business_user", "reviewer", "rating",
            "description", "created_at", "updated_at",
        ]
        for field in expected_fields:
            self.assertIn(field, response.data[0])

    # --- Filtering ---

    def test_reviews_list_filter_by_business_user_id(self):
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.customer_token.key)
        response = self.client.get(self.url, {"business_user_id": self.business_user_1.id})
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["business_user"], self.business_user_1.id)

    def test_reviews_list_filter_by_reviewer_id(self):
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.customer_token.key)
        response = self.client.get(self.url, {"reviewer_id": self.customer_user.id})
        self.assertEqual(len(response.data), 2)

    def test_reviews_list_ordering_by_rating(self):
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.customer_token.key)
        response = self.client.get(self.url, {"ordering": "rating"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        ratings = [r["rating"] for r in response.data]
        self.assertEqual(ratings, sorted(ratings))

    def test_reviews_list_ordering_by_updated_at(self):
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.customer_token.key)
        response = self.client.get(self.url, {"ordering": "updated_at"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    # --- 401 Not authenticated ---

    def test_reviews_list_returns_401_if_not_authenticated(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)