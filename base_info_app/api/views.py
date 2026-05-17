"""
Views for base information endpoints.
"""

from django.db.models import Avg

from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from offers_app.models import Offer
from profiles_app.models import UserProfile
from reviews_app.models import Review


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

        review_count = Review.objects.count()

        average_rating = Review.objects.aggregate(
            avg=Avg("rating")
        )["avg"]

        average_rating = (
            round(average_rating, 1)
            if average_rating is not None
            else 0.0
        )

        business_profile_count = UserProfile.objects.filter(
            type="business"
        ).count()

        offer_count = Offer.objects.count()

        return Response(
            {
                "review_count": review_count,
                "average_rating": average_rating,
                "business_profile_count": (
                    business_profile_count
                ),
                "offer_count": offer_count,
            },
            status=status.HTTP_200_OK,
        )