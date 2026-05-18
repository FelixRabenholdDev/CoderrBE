"""
Views for base information endpoints.
"""
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .filters import (
    get_average_rating,
    get_business_profile_count,
    get_offer_count,
    get_review_count,
)


class BaseInfoView(APIView):
    """
    API view for retrieving platform base information.
    """

    permission_classes = [AllowAny]

    def get(self, request):
        """
        Handle GET requests for platform statistics.

        Args:
            request: Incoming HTTP request.

        Returns:
            Response:
                HTTP response containing platform statistics.
        """

        return Response(
            {
                "review_count": get_review_count(),
                "average_rating": get_average_rating(),
                "business_profile_count": (
                    get_business_profile_count()
                ),
                "offer_count": get_offer_count(),
            },
            status=status.HTTP_200_OK,
        )