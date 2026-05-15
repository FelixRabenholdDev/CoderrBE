from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token
from reviews_app.models import Review
from profiles_app.models import UserProfile


class ReviewsCreateAPITest(APITestCase):

    def setUp(self):
        self.url = reverse("reviews-list")

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

        self.valid_payload = {
            "business_user": self.business_user.id,
            "rating": 4,
            "description": "Alles war toll!",
        }

    # --- 201 Happy Path ---

    def test_reviews_create_returns_201(self):
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.customer_token.key)
        response = self.client.post(self.url, self.valid_payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_reviews_create_returns_correct_fields(self):
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.customer_token.key)
        response = self.client.post(self.url, self.valid_payload, format="json")
        expected_fields = [
            "id", "business_user", "reviewer", "rating",
            "description", "created_at", "updated_at",
        ]
        for field in expected_fields:
            self.assertIn(field, response.data)

    def test_reviews_create_sets_reviewer_to_current_user(self):
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.customer_token.key)
        response = self.client.post(self.url, self.valid_payload, format="json")
        self.assertEqual(response.data["reviewer"], self.customer_user.id)

    def test_reviews_create_persists_to_db(self):
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.customer_token.key)
        self.client.post(self.url, self.valid_payload, format="json")
        self.assertEqual(Review.objects.count(), 1)

    # --- 400 Bad Request ---

    def test_reviews_create_fails_if_rating_missing(self):
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.customer_token.key)
        payload = {k: v for k, v in self.valid_payload.items() if k != "rating"}
        response = self.client.post(self.url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_reviews_create_fails_if_business_user_missing(self):
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.customer_token.key)
        payload = {k: v for k, v in self.valid_payload.items() if k != "business_user"}
        response = self.client.post(self.url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # --- 401 Not authenticated ---

    def test_reviews_create_returns_401_if_not_authenticated(self):
        response = self.client.post(self.url, self.valid_payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # --- 403 Not a customer ---

    def test_reviews_create_returns_403_if_business_user(self):
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.business_token.key)
        response = self.client.post(self.url, self.valid_payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_reviews_create_returns_403_if_duplicate_review(self):
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.customer_token.key)
        self.client.post(self.url, self.valid_payload, format="json")
        response = self.client.post(self.url, self.valid_payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)