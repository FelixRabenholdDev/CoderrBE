from django.urls import path
from .views import ProfileDetailView, BusinessProfilesView, CustomerProfilesView

urlpatterns = [
    path('profile/<int:pk>/', ProfileDetailView.as_view(), name='profile-detail'),
    path('profiles/business/', BusinessProfilesView.as_view(), name='profiles-business'),
    path('profiles/customer/', CustomerProfilesView.as_view(), name='profiles-customer'),
]