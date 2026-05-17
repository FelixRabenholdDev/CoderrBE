"""
URL configuration for review-related endpoints.
"""

from django.urls import path

from .views import (
    ReviewDetailView,
    ReviewsListView,
)


urlpatterns = [
    path(
        "reviews/",
        ReviewsListView.as_view(),
        name="reviews-list",
    ),
    path(
        "reviews/<int:pk>/",
        ReviewDetailView.as_view(),
        name="review-detail",
    ),
]