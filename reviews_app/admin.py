from django.contrib import admin
from .models import Review


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "business_user",
        "reviewer",
        "rating",
        "created_at",
        "updated_at",
    )

    search_fields = (
        "business_user__username",
        "business_user__email",
        "reviewer__username",
        "reviewer__email",
        "description",
    )

    list_filter = (
        "rating",
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
        "business_user",
        "reviewer",
    )

    fieldsets = (
        (
            "Review Information",
            {
                "fields": (
                    "rating",
                    "description",
                )
            },
        ),
        (
            "Users",
            {
                "fields": (
                    "business_user",
                    "reviewer",
                )
            },
        ),
        (
            "Metadata",
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
            "business_user",
            "reviewer",
        )