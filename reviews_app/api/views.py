"""
Views for review management endpoints.
"""

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from reviews_app.models import Review
from profiles_app.models import UserProfile

from .serializers import (
    ReviewPatchSerializer,
    ReviewSerializer,
)


class ReviewsListView(APIView):
    """
    API view for listing and creating reviews.
    """

    def get(self, request):
        """
        Handle GET requests for retrieving reviews.

        Supports filtering and ordering.

        Args:
            request: Incoming HTTP request.

        Returns:
            Response:
                List of reviews.
        """

        queryset = Review.objects.all()

        business_user_id = request.query_params.get(
            "business_user_id"
        )

        if business_user_id:
            queryset = queryset.filter(
                business_user__id=business_user_id
            )

        reviewer_id = request.query_params.get(
            "reviewer_id"
        )

        if reviewer_id:
            queryset = queryset.filter(
                reviewer__id=reviewer_id
            )

        ordering = request.query_params.get(
            "ordering"
        )

        if ordering in ["rating", "updated_at"]:
            queryset = queryset.order_by(ordering)
        else:
            queryset = queryset.order_by("updated_at")

        serializer = ReviewSerializer(
            queryset,
            many=True,
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )

    def post(self, request):
        """
        Handle POST requests for creating reviews.

        Args:
            request: Incoming HTTP request.

        Returns:
            Response:
                Created review or error message.
        """

        try:
            profile = UserProfile.objects.get(
                user=request.user
            )

            if profile.type != "customer":
                return Response(
                    {
                        "detail": (
                            "Nur Customer-User dürfen "
                            "Bewertungen erstellen."
                        )
                    },
                    status=status.HTTP_403_FORBIDDEN,
                )

        except UserProfile.DoesNotExist:
            return Response(
                {
                    "detail": (
                        "Profil nicht gefunden."
                    )
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        business_user_id = request.data.get(
            "business_user"
        )

        if Review.objects.filter(
            reviewer=request.user,
            business_user__id=business_user_id,
        ).exists():
            return Response(
                {
                    "detail": (
                        "Du hast bereits eine "
                        "Bewertung für diesen "
                        "Geschäftsbenutzer abgegeben."
                    )
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = ReviewSerializer(
            data=request.data
        )

        if serializer.is_valid():
            serializer.save(
                reviewer=request.user
            )

            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED,
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )


class ReviewDetailView(APIView):
    """
    API view for updating and deleting reviews.
    """

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

        if review.reviewer != request.user:
            return Response(
                {"detail": "Nicht erlaubt."},
                status=status.HTTP_403_FORBIDDEN,
            )

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

        if review.reviewer != request.user:
            return Response(
                {"detail": "Nicht erlaubt."},
                status=status.HTTP_403_FORBIDDEN,
            )

        review.delete()

        return Response(
            status=status.HTTP_204_NO_CONTENT
        )