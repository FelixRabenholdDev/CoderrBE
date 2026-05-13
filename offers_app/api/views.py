from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.db.models import Min, Q

from offers_app.models import Offer, OfferDetail
from .serializers import (
    OfferListSerializer, OfferCreateSerializer,
    OfferRetrieveSerializer, OfferPatchSerializer,
    OfferDetailSerializer,
)
from profiles_app.models import UserProfile


class OffersListView(APIView):

    def get_permissions(self):
        if self.request.method == "GET":
            return [AllowAny()]
        return [IsAuthenticated()]

    def get(self, request):
        queryset = Offer.objects.all().annotate(
            min_price=Min("details__price"),
            min_delivery_time=Min("details__delivery_time_in_days"),
        ).order_by("created_at")

        creator_id = request.query_params.get("creator_id")
        if creator_id:
            queryset = queryset.filter(user__id=creator_id)

        min_price = request.query_params.get("min_price")
        if min_price:
            queryset = queryset.filter(min_price__gte=min_price)

        max_delivery_time = request.query_params.get("max_delivery_time")
        if max_delivery_time:
            queryset = queryset.filter(min_delivery_time__lte=max_delivery_time)

        search = request.query_params.get("search")
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) | Q(description__icontains=search)
            )

        ordering = request.query_params.get("ordering")
        if ordering == "min_price":
            queryset = queryset.order_by("min_price")
        elif ordering == "updated_at":
            queryset = queryset.order_by("updated_at")

        from rest_framework.pagination import PageNumberPagination
        paginator = PageNumberPagination()
        page_size = request.query_params.get("page_size", 6)
        paginator.page_size = page_size
        page = paginator.paginate_queryset(queryset, request)
        serializer = OfferListSerializer(page, many=True, context={"request": request})
        return paginator.get_paginated_response(serializer.data)

    def post(self, request):
        try:
            profile = UserProfile.objects.get(user=request.user)
            if profile.type != "business":
                return Response(
                    {"detail": "Nur Business-User dürfen Angebote erstellen."},
                    status=status.HTTP_403_FORBIDDEN,
                )
        except UserProfile.DoesNotExist:
            return Response({"detail": "Profil nicht gefunden."}, status=status.HTTP_403_FORBIDDEN)

        serializer = OfferCreateSerializer(data=request.data)
        if serializer.is_valid():
            offer = serializer.save(user=request.user)
            return Response(OfferCreateSerializer(offer).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class OfferDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get_offer(self, pk):
        try:
            return Offer.objects.get(pk=pk)
        except Offer.DoesNotExist:
            return None

    def get(self, request, pk):
        offer = self.get_offer(pk)
        if not offer:
            return Response({"detail": "Nicht gefunden."}, status=status.HTTP_404_NOT_FOUND)
        serializer = OfferRetrieveSerializer(offer, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, pk):
        offer = self.get_offer(pk)
        if not offer:
            return Response({"detail": "Nicht gefunden."}, status=status.HTTP_404_NOT_FOUND)
        if offer.user != request.user:
            return Response({"detail": "Nicht erlaubt."}, status=status.HTTP_403_FORBIDDEN)
        serializer = OfferPatchSerializer(offer, data=request.data, partial=True)
        if serializer.is_valid():
            updated_offer = serializer.save()
            return Response(OfferPatchSerializer(updated_offer).data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        offer = self.get_offer(pk)
        if not offer:
            return Response({"detail": "Nicht gefunden."}, status=status.HTTP_404_NOT_FOUND)
        if offer.user != request.user:
            return Response({"detail": "Nicht erlaubt."}, status=status.HTTP_403_FORBIDDEN)
        offer.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class OfferDetailItemView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        try:
            offer_detail = OfferDetail.objects.get(pk=pk)
        except OfferDetail.DoesNotExist:
            return Response({"detail": "Nicht gefunden."}, status=status.HTTP_404_NOT_FOUND)
        serializer = OfferDetailSerializer(offer_detail)
        return Response(serializer.data, status=status.HTTP_200_OK)