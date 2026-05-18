from rest_framework.permissions import BasePermission


class IsReviewOwner(BasePermission):
    """
    Allows access only to the reviewer who created the review.
    """

    def has_object_permission(self, request, view, obj):
        return obj.reviewer == request.user