from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token
from reviews_app.models import Review
from profiles_app.models import UserProfile


class ReviewsDeleteAPITest(APITestCase):

    def setUp(self):
        self.customer_user = User.objects.create_user(
            username="customer_user",
            email="customer@mail.de",
            password="securePassword123",
        )
        UserProfile.objects.create(user=self.customer_user, type="customer")
        self.customer_token = Token.objects.create(user=self.customer_user)

        self.other_customer = User.objects.create_user(
            username="other_customer",
            email="other@mail.de",
            password="securePassword123",
        )
        UserProfile.objects.create(user=self.other_customer, type="customer")
        self.other_token = Token.objects.create(user=self.other_customer)

        self.business_user = User.objects.create_user(
            username="business_user",
            email="business@mail.de",
            password="securePassword123",
        )
        UserProfile.objects.create(user=self.business_user, type="business")

        self.review = Review.objects.create(
            business_user=self.business_user,
            reviewer=self.customer_user,
            rating=4,
            description="Sehr gut!",
        )
        self.url = reverse("review-detail", kwargs={"pk": self.review.pk})

    # --- 204 Happy Path ---

    def test_reviews_delete_returns_204(self):
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.customer_token.key)
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_reviews_delete_removes_from_db(self):
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.customer_token.key)
        self.client.delete(self.url)
        self.assertEqual(Review.objects.count(), 0)

    def test_reviews_delete_returns_no_content(self):
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.customer_token.key)
        response = self.client.delete(self.url)
        self.assertEqual(len(response.content), 0)

    # --- 401 Not authenticated ---

    def test_reviews_delete_returns_401_if_not_authenticated(self):
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # --- 403 Not owner ---

    def test_reviews_delete_returns_403_if_not_owner(self):
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.other_token.key)
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # --- 404 Not found ---

    def test_reviews_delete_returns_404_if_not_found(self):
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.customer_token.key)
        url = reverse("review-detail", kwargs={"pk": 99999})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)