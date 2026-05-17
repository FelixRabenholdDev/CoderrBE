"""
URL configuration for profile-related endpoints.
"""

from django.urls import path

from .views import (
    BusinessProfilesView,
    CustomerProfilesView,
    ProfileDetailView,
)


urlpatterns = [
    path(
        "profile/<int:pk>/",
        ProfileDetailView.as_view(),
        name="profile-detail",
    ),
    path(
        "profiles/business/",
        BusinessProfilesView.as_view(),
        name="profiles-business",
    ),
    path(
        "profiles/customer/",
        CustomerProfilesView.as_view(),
        name="profiles-customer",
    ),
]