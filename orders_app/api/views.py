"""
Views for order management endpoints.
"""

from django.contrib.auth.models import User
from django.db.models import Q

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

from offers_app.models import OfferDetail
from orders_app.models import Order
from core.permissions import IsCustomerUser, IsAdminUser
from .permissions import IsOrderBusinessUser

from .serializers import (
    OrderSerializer,
    OrderStatusPatchSerializer,
)


class OrdersListView(APIView):
    """
    API view for listing and creating orders.
    """

    def get_permissions(self):
        """
        Return permissions depending on request method.

        Returns:
            list: Permission classes for the request.
        """
        if self.request.method == "POST":
            return [IsCustomerUser()]
        return [IsAuthenticated()]

    def get(self, request):
        """
        Handle GET requests for retrieving orders.

        Args:
            request: Incoming HTTP request.

        Returns:
            Response:
                List of user-related orders.
        """

        orders = Order.objects.filter(
            Q(customer_user=request.user)
            | Q(business_user=request.user)
        ).order_by("created_at")

        serializer = OrderSerializer(
            orders,
            many=True,
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )

    def post(self, request):
        """
        Handle POST requests for creating orders.

        Args:
            request: Incoming HTTP request.

        Returns:
            Response:
                Created order data or error message.
        """

        offer_detail_id = request.data.get(
            "offer_detail_id"
        )

        if not offer_detail_id:
            return Response(
                {
                    "detail": (
                        "offer_detail_id ist "
                        "erforderlich."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            offer_detail = OfferDetail.objects.get(
                pk=offer_detail_id
            )

        except OfferDetail.DoesNotExist:
            return Response(
                {
                    "detail": (
                        "Angebotsdetail nicht "
                        "gefunden."
                    )
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        order = Order.objects.create(
            customer_user=request.user,
            business_user=offer_detail.offer.user,
            title=offer_detail.title,
            revisions=offer_detail.revisions,
            delivery_time_in_days=(
                offer_detail.delivery_time_in_days
            ),
            price=offer_detail.price,
            features=offer_detail.features,
            offer_type=offer_detail.offer_type,
        )

        serializer = OrderSerializer(order)

        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED,
        )


class OrderDetailView(APIView):
    """
    API view for updating and deleting orders.
    """

    def get_permissions(self):
        """
        Return permissions depending on request method.

        Returns:
            list: Permission classes for the request.
        """
        if self.request.method == "PATCH":
            return [IsOrderBusinessUser()]
        if self.request.method == "DELETE":
            return [IsAdminUser()]
        return []

    def get_order(self, pk):
        """
        Retrieve an order by primary key.

        Args:
            pk (int): Order primary key.

        Returns:
            Order | None:
                Order instance or None.
        """

        try:
            return Order.objects.get(pk=pk)

        except Order.DoesNotExist:
            return None

    def patch(self, request, pk):
        """
        Handle PATCH requests for updating
        order status.

        Args:
            request: Incoming HTTP request.
            pk (int): Order primary key.

        Returns:
            Response:
                Updated order data or error message.
        """

        order = self.get_order(pk)

        if not order:
            return Response(
                {"detail": "Nicht gefunden."},
                status=status.HTTP_404_NOT_FOUND,
            )

        self.check_object_permissions(request, order)

        serializer = OrderStatusPatchSerializer(
            order,
            data=request.data,
            partial=True,
        )

        if serializer.is_valid():
            serializer.save()

            return Response(
                OrderSerializer(order).data,
                status=status.HTTP_200_OK,
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )

    def delete(self, request, pk):
        """
        Handle DELETE requests for orders.

        Args:
            request: Incoming HTTP request.
            pk (int): Order primary key.

        Returns:
            Response:
                Empty response or error message.
        """

        order = self.get_order(pk)

        if not order:
            return Response(
                {"detail": "Nicht gefunden."},
                status=status.HTTP_404_NOT_FOUND,
            )

        # if not request.user.is_staff:
        #     return Response(
        #         {"detail": "Keine Berechtigung."},
        #         status=status.HTTP_403_FORBIDDEN,
        #     )

        order.delete()

        return Response(
            status=status.HTTP_204_NO_CONTENT
        )


class OrderCountView(APIView):
    """
    API view for retrieving active order count.
    """

    def get(self, request, business_user_id):
        """
        Handle GET requests for active order count.

        Args:
            request: Incoming HTTP request.
            business_user_id (int):
                Business user primary key.

        Returns:
            Response:
                Count of active orders.
        """

        try:
            business_user = User.objects.get(
                pk=business_user_id
            )

        except User.DoesNotExist:
            return Response(
                {
                    "detail": (
                        "Business-User nicht "
                        "gefunden."
                    )
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        count = Order.objects.filter(
            business_user=business_user,
            status="in_progress",
        ).count()

        return Response(
            {"order_count": count},
            status=status.HTTP_200_OK,
        )


class CompletedOrderCountView(APIView):
    """
    API view for retrieving completed order count.
    """

    def get(self, request, business_user_id):
        """
        Handle GET requests for completed order count.

        Args:
            request: Incoming HTTP request.
            business_user_id (int):
                Business user primary key.

        Returns:
            Response:
                Count of completed orders.
        """

        try:
            business_user = User.objects.get(
                pk=business_user_id
            )

        except User.DoesNotExist:
            return Response(
                {
                    "detail": (
                        "Business-User nicht "
                        "gefunden."
                    )
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        count = Order.objects.filter(
            business_user=business_user,
            status="completed",
        ).count()

        return Response(
            {"completed_order_count": count},
            status=status.HTTP_200_OK,
        )