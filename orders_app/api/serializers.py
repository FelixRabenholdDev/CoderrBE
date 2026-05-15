from rest_framework import serializers
from orders_app.models import Order


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = [
            "id", "customer_user", "business_user", "title", "revisions",
            "delivery_time_in_days", "price", "features", "offer_type",
            "status", "created_at", "updated_at",
        ]
        read_only_fields = [
            "id", "customer_user", "business_user", "title", "revisions",
            "delivery_time_in_days", "price", "features", "offer_type",
            "created_at", "updated_at",
        ]


class OrderStatusPatchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ["status"]

    def validate_status(self, value):
        allowed = ["in_progress", "completed", "cancelled"]
        if value not in allowed:
            raise serializers.ValidationError(f"Status muss einer von {allowed} sein.")
        return value