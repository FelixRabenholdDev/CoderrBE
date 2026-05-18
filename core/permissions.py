from rest_framework.permissions import BasePermission
from profiles_app.models import UserProfile


class IsCustomerUser(BasePermission):
    """
    Allows access only to users with a customer profile.
    """

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        try:
            profile = UserProfile.objects.get(user=request.user)
            return profile.type == "customer"
        except UserProfile.DoesNotExist:
            return False


class IsBusinessUser(BasePermission):
    """
    Allows access only to users with a business profile.
    """

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        try:
            profile = UserProfile.objects.get(user=request.user)
            return profile.type == "business"
        except UserProfile.DoesNotExist:
            return False


class IsAdminUser(BasePermission):
    """
    Allows access only to staff/admin users.
    """

    def has_permission(self, request, view):
        return request.user and request.user.is_staff