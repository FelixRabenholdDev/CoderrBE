from rest_framework.permissions import BasePermission


class IsOrderBusinessUser(BasePermission):
    """
    Allows access only to the business user assigned to the order.
    """

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        return obj.business_user == request.user