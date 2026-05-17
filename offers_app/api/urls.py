"""
URL configuration for offer-related endpoints.
"""

from django.urls import path

from .views import (
    OfferDetailItemView,
    OfferDetailView,
    OffersListView,
)


urlpatterns = [
    path(
        "offers/",
        OffersListView.as_view(),
        name="offers-list",
    ),
    path(
        "offers/<int:pk>/",
        OfferDetailView.as_view(),
        name="offer-detail",
    ),
    path(
        "offerdetails/<int:pk>/",
        OfferDetailItemView.as_view(),
        name="offerdetail-detail",
    ),
]