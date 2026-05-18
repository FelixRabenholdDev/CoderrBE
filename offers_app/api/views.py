"""
Views for offer management and offer detail endpoints.
"""

from django.db.models import Min

from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from offers_app.models import Offer, OfferDetail
from core.permissions import IsBusinessUser
from .filters import filter_offers
from .permissions import IsOfferOwner

from .serializers import (
    OfferCreateSerializer,
    OfferDetailSerializer,
    OfferListSerializer,
    OfferPatchSerializer,
    OfferRetrieveSerializer,
)


class OffersListView(APIView):
    """
    API view for listing and creating offers.
    """

    def get_permissions(self):
        """
        Return permissions depending on request method.

        Returns:
            list: Permission classes for the request.
        """

        if self.request.method == "GET":
            return [AllowAny()]

        return [IsBusinessUser()]

    def get(self, request):
        """
        Handle GET requests for retrieving offers.

        Supports filtering, searching, ordering,
        and pagination.

        Args:
            request: Incoming HTTP request.

        Returns:
            Response:
                Paginated list of offers.
        """

        queryset = Offer.objects.all().annotate(
            min_price=Min("details__price"),
            min_delivery_time=Min(
                "details__delivery_time_in_days"
            ),
        ).order_by("created_at")
        
        queryset = filter_offers(queryset, request)

        paginator = PageNumberPagination()

        page_size = request.query_params.get(
            "page_size",
            6,
        )

        paginator.page_size = page_size

        page = paginator.paginate_queryset(
            queryset,
            request,
        )

        serializer = OfferListSerializer(
            page,
            many=True,
            context={"request": request},
        )

        return paginator.get_paginated_response(
            serializer.data
        )

    def post(self, request):
        """
        Handle POST requests for creating offers.

        Args:
            request: Incoming HTTP request.

        Returns:
            Response:
                Created offer data or validation errors.
        """

        serializer = OfferCreateSerializer(
            data=request.data
        )

        if serializer.is_valid():
            offer = serializer.save(
                user=request.user
            )

            return Response(
                OfferCreateSerializer(offer).data,
                status=status.HTTP_201_CREATED,
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )


class OfferDetailView(APIView):
    """
    API view for retrieving, updating,
    and deleting offers.
    """

    permission_classes = [IsOfferOwner]

    def get_offer(self, pk):
        """
        Retrieve an offer by primary key.

        Args:
            pk (int): Offer primary key.

        Returns:
            Offer | None:
                Offer instance or None if not found.
        """

        try:
            return Offer.objects.get(pk=pk)

        except Offer.DoesNotExist:
            return None

    def get(self, request, pk):
        """
        Handle GET requests for a single offer.

        Args:
            request: Incoming HTTP request.
            pk (int): Offer primary key.

        Returns:
            Response:
                Offer data or error message.
        """

        offer = self.get_offer(pk)

        if not offer:
            return Response(
                {"detail": "Nicht gefunden."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = OfferRetrieveSerializer(
            offer,
            context={"request": request},
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )

    def patch(self, request, pk):
        """
        Handle PATCH requests for updating offers.

        Args:
            request: Incoming HTTP request.
            pk (int): Offer primary key.

        Returns:
            Response:
                Updated offer data or error message.
        """

        offer = self.get_offer(pk)

        if not offer:
            return Response(
                {"detail": "Nicht gefunden."},
                status=status.HTTP_404_NOT_FOUND,
            )

        self.check_object_permissions(request, offer)

        serializer = OfferPatchSerializer(
            offer,
            data=request.data,
            partial=True,
        )

        if serializer.is_valid():
            updated_offer = serializer.save()

            return Response(
                OfferPatchSerializer(
                    updated_offer
                ).data,
                status=status.HTTP_200_OK,
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )

    def delete(self, request, pk):
        """
        Handle DELETE requests for offers.

        Args:
            request: Incoming HTTP request.
            pk (int): Offer primary key.

        Returns:
            Response:
                Empty response or error message.
        """

        offer = self.get_offer(pk)

        if not offer:
            return Response(
                {"detail": "Nicht gefunden."},
                status=status.HTTP_404_NOT_FOUND,
            )

        self.check_object_permissions(request, offer)

        offer.delete()

        return Response(
            status=status.HTTP_204_NO_CONTENT
        )


class OfferDetailItemView(APIView):
    """
    API view for retrieving offer detail items.
    """

    def get(self, request, pk):
        """
        Handle GET requests for offer detail items.

        Args:
            request: Incoming HTTP request.
            pk (int): OfferDetail primary key.

        Returns:
            Response:
                Offer detail data or error message.
        """

        try:
            offer_detail = OfferDetail.objects.get(
                pk=pk
            )

        except OfferDetail.DoesNotExist:
            return Response(
                {"detail": "Nicht gefunden."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = OfferDetailSerializer(
            offer_detail
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )