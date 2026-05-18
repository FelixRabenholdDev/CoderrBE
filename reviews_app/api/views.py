"""
Views for review management endpoints.
"""

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from reviews_app.models import Review
from core.permissions import IsCustomerUser
from reviews_app.api.permissions import IsReviewOwner

from .filters import filter_reviews
from .serializers import (
    ReviewPatchSerializer,
    ReviewSerializer,
)


class ReviewsListView(APIView):
    """
    API view for listing and creating reviews.
    """

    def get_permissions(self):
        if self.request.method == "POST":
            return [IsCustomerUser()]
        return [IsAuthenticated()]

    def get(self, request):
        """
        Handle GET requests for retrieving reviews.

        Args:
            request: Incoming HTTP request.

        Returns:
            Response:
                List of reviews.
        """
        queryset = Review.objects.all()
        queryset = filter_reviews(queryset, request)
        serializer = ReviewSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        """
        Handle POST requests for creating reviews.

        Args:
            request: Incoming HTTP request.

        Returns:
            Response:
                Created review or error message.
        """

        serializer = ReviewSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        business_user_id = request.data.get(
            "business_user"
        )

        if Review.objects.filter(
            reviewer=request.user,
            business_user__id=business_user_id,
        ).exists():
            return Response(
                {"detail": "Du hast bereits eine Bewertung für diesen Geschäftsbenutzer abgegeben."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer.save(reviewer=request.user)
        
        return Response(
            serializer.data, 
            status=status.HTTP_201_CREATED,
        )

class ReviewDetailView(APIView):
    """
    API view for updating and deleting reviews.
    """

    permission_classes = [IsReviewOwner]

    def get_review(self, pk):
        """
        Retrieve a review by primary key.

        Args:
            pk (int): Review primary key.

        Returns:
            Review | None:
                Review instance or None.
        """

        try:
            return Review.objects.get(pk=pk)

        except Review.DoesNotExist:
            return None

    def patch(self, request, pk):
        """
        Handle PATCH requests for updating reviews.

        Args:
            request: Incoming HTTP request.
            pk (int): Review primary key.

        Returns:
            Response:
                Updated review or error message.
        """

        review = self.get_review(pk)

        if not review:
            return Response(
                {"detail": "Nicht gefunden."},
                status=status.HTTP_404_NOT_FOUND,
            )

        self.check_object_permissions(request, review)

        serializer = ReviewPatchSerializer(
            review,
            data=request.data,
            partial=True,
        )

        if serializer.is_valid():
            serializer.save()

            return Response(
                ReviewSerializer(review).data,
                status=status.HTTP_200_OK,
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )

    def delete(self, request, pk):
        """
        Handle DELETE requests for reviews.

        Args:
            request: Incoming HTTP request.
            pk (int): Review primary key.

        Returns:
            Response:
                Empty response or error message.
        """

        review = self.get_review(pk)

        if not review:
            return Response(
                {"detail": "Nicht gefunden."},
                status=status.HTTP_404_NOT_FOUND,
            )

        self.check_object_permissions(request, review)

        review.delete()

        return Response(
            status=status.HTTP_204_NO_CONTENT
        )