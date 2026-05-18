from django.contrib import admin
from .models import Order


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "title",
        "customer_user",
        "business_user",
        "offer_type",
        "price",
        "status",
        "created_at",
    )

    search_fields = (
        "title",
        "customer_user__username",
        "customer_user__email",
        "business_user__username",
        "business_user__email",
    )

    list_filter = (
        "status",
        "offer_type",
        "created_at",
        "updated_at",
    )

    ordering = (
        "-created_at",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )

    autocomplete_fields = (
        "customer_user",
        "business_user",
    )

    fieldsets = (
        (
            "Order Information",
            {
                "fields": (
                    "title",
                    "status",
                    "offer_type",
                )
            },
        ),
        (
            "Users",
            {
                "fields": (
                    "customer_user",
                    "business_user",
                )
            },
        ),
        (
            "Pricing & Delivery",
            {
                "fields": (
                    "price",
                    "delivery_time_in_days",
                    "revisions",
                )
            },
        ),
        (
            "Features",
            {
                "fields": (
                    "features",
                )
            },
        ),
        (
            "Timestamps",
            {
                "fields": (
                    "created_at",
                    "updated_at",
                )
            },
        ),
    )

    def get_queryset(self, request):
        queryset = super().get_queryset(request)

        return queryset.select_related(
            "customer_user",
            "business_user",
        )