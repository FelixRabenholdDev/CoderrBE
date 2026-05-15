from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.models import User
from django.db.models import Q

from orders_app.models import Order
from .serializers import OrderSerializer, OrderStatusPatchSerializer
from offers_app.models import OfferDetail
from profiles_app.models import UserProfile


class OrdersListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        orders = Order.objects.filter(
            Q(customer_user=request.user) | Q(business_user=request.user)
        ).order_by("created_at")
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        try:
            profile = UserProfile.objects.get(user=request.user)
            if profile.type != "customer":
                return Response(
                    {"detail": "Nur Customer-User dürfen Bestellungen erstellen."},
                    status=status.HTTP_403_FORBIDDEN,
                )
        except UserProfile.DoesNotExist:
            return Response({"detail": "Profil nicht gefunden."}, status=status.HTTP_403_FORBIDDEN)

        offer_detail_id = request.data.get("offer_detail_id")
        if not offer_detail_id:
            return Response({"detail": "offer_detail_id ist erforderlich."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            offer_detail = OfferDetail.objects.get(pk=offer_detail_id)
        except OfferDetail.DoesNotExist:
            return Response({"detail": "Angebotsdetail nicht gefunden."}, status=status.HTTP_404_NOT_FOUND)

        order = Order.objects.create(
            customer_user=request.user,
            business_user=offer_detail.offer.user,
            title=offer_detail.title,
            revisions=offer_detail.revisions,
            delivery_time_in_days=offer_detail.delivery_time_in_days,
            price=offer_detail.price,
            features=offer_detail.features,
            offer_type=offer_detail.offer_type,
        )
        serializer = OrderSerializer(order)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class OrderDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get_order(self, pk):
        try:
            return Order.objects.get(pk=pk)
        except Order.DoesNotExist:
            return None

    def patch(self, request, pk):
        order = self.get_order(pk)
        if not order:
            return Response({"detail": "Nicht gefunden."}, status=status.HTTP_404_NOT_FOUND)

        try:
            profile = UserProfile.objects.get(user=request.user)
            if profile.type != "business":
                return Response({"detail": "Nur Business-User dürfen den Status ändern."}, status=status.HTTP_403_FORBIDDEN)
        except UserProfile.DoesNotExist:
            return Response({"detail": "Profil nicht gefunden."}, status=status.HTTP_403_FORBIDDEN)

        if order.business_user != request.user:
            return Response({"detail": "Nicht erlaubt."}, status=status.HTTP_403_FORBIDDEN)

        serializer = OrderStatusPatchSerializer(order, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(OrderSerializer(order).data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        order = self.get_order(pk)
        if not order:
            return Response({"detail": "Nicht gefunden."}, status=status.HTTP_404_NOT_FOUND)

        if not request.user.is_staff:
            return Response({"detail": "Keine Berechtigung."}, status=status.HTTP_403_FORBIDDEN)

        order.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class OrderCountView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, business_user_id):
        try:
            business_user = User.objects.get(pk=business_user_id)
        except User.DoesNotExist:
            return Response({"detail": "Business-User nicht gefunden."}, status=status.HTTP_404_NOT_FOUND)

        count = Order.objects.filter(business_user=business_user, status="in_progress").count()
        return Response({"order_count": count}, status=status.HTTP_200_OK)


class CompletedOrderCountView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, business_user_id):
        try:
            business_user = User.objects.get(pk=business_user_id)
        except User.DoesNotExist:
            return Response({"detail": "Business-User nicht gefunden."}, status=status.HTTP_404_NOT_FOUND)

        count = Order.objects.filter(business_user=business_user, status="completed").count()
        return Response({"completed_order_count": count}, status=status.HTTP_200_OK)