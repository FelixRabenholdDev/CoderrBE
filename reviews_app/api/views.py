from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from reviews_app.models import Review
from .serializers import ReviewSerializer, ReviewPatchSerializer
from profiles_app.models import UserProfile


class ReviewsListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        queryset = Review.objects.all()

        business_user_id = request.query_params.get("business_user_id")
        if business_user_id:
            queryset = queryset.filter(business_user__id=business_user_id)

        reviewer_id = request.query_params.get("reviewer_id")
        if reviewer_id:
            queryset = queryset.filter(reviewer__id=reviewer_id)

        ordering = request.query_params.get("ordering")
        if ordering in ["rating", "updated_at"]:
            queryset = queryset.order_by(ordering)
        else:
            queryset = queryset.order_by("updated_at")

        serializer = ReviewSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        try:
            profile = UserProfile.objects.get(user=request.user)
            if profile.type != "customer":
                return Response(
                    {"detail": "Nur Customer-User dürfen Bewertungen erstellen."},
                    status=status.HTTP_403_FORBIDDEN,
                )
        except UserProfile.DoesNotExist:
            return Response({"detail": "Profil nicht gefunden."}, status=status.HTTP_403_FORBIDDEN)

        business_user_id = request.data.get("business_user")
        if Review.objects.filter(
            reviewer=request.user, business_user__id=business_user_id
        ).exists():
            return Response(
                {"detail": "Du hast bereits eine Bewertung für diesen Geschäftsbenutzer abgegeben."},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = ReviewSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(reviewer=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ReviewDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get_review(self, pk):
        try:
            return Review.objects.get(pk=pk)
        except Review.DoesNotExist:
            return None

    def patch(self, request, pk):
        review = self.get_review(pk)
        if not review:
            return Response({"detail": "Nicht gefunden."}, status=status.HTTP_404_NOT_FOUND)

        if review.reviewer != request.user:
            return Response({"detail": "Nicht erlaubt."}, status=status.HTTP_403_FORBIDDEN)

        serializer = ReviewPatchSerializer(review, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(ReviewSerializer(review).data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        review = self.get_review(pk)
        if not review:
            return Response({"detail": "Nicht gefunden."}, status=status.HTTP_404_NOT_FOUND)

        if review.reviewer != request.user:
            return Response({"detail": "Nicht erlaubt."}, status=status.HTTP_403_FORBIDDEN)

        review.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)