from rest_framework.permissions import BasePermission


class IsOfferOwner(BasePermission):
    """
    Allows access only to the user who created the offer.
    """

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        return obj.user == request.user