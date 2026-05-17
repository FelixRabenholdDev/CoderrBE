"""
Serializers for order management.
"""

from rest_framework import serializers

from orders_app.models import Order


class OrderSerializer(serializers.ModelSerializer):
    """
    Serializer for order objects.
    """

    class Meta:
        """
        Meta configuration for OrderSerializer.
        """

        model = Order

        fields = [
            "id",
            "customer_user",
            "business_user",
            "title",
            "revisions",
            "delivery_time_in_days",
            "price",
            "features",
            "offer_type",
            "status",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "customer_user",
            "business_user",
            "title",
            "revisions",
            "delivery_time_in_days",
            "price",
            "features",
            "offer_type",
            "created_at",
            "updated_at",
        ]


class OrderStatusPatchSerializer(
    serializers.ModelSerializer
):
    """
    Serializer for updating order status.
    """

    class Meta:
        """
        Meta configuration for
        OrderStatusPatchSerializer.
        """

        model = Order
        fields = ["status"]

    def validate_status(self, value):
        """
        Validate the order status value.

        Args:
            value (str): Incoming status value.

        Returns:
            str: Validated status value.

        Raises:
            serializers.ValidationError:
                If the status value is invalid.
        """

        allowed = [
            "in_progress",
            "completed",
            "cancelled",
        ]

        if value not in allowed:
            raise serializers.ValidationError(
                (
                    "Status muss einer von "
                    f"{allowed} sein."
                )
            )

        return value