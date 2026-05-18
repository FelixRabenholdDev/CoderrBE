from rest_framework.permissions import BasePermission


class IsProfileOwner(BasePermission):
    """
    Allows access only to the user who owns the profile.
    """

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        return obj.user == request.user