from django.contrib import admin
from .models import UserProfile


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "type",
        "location",
        "tel",
        "created_at",
    )

    search_fields = (
        "user__username",
        "user__email",
        "location",
        "tel",
    )

    list_filter = (
        "type",
        "created_at",
    )

    ordering = (
        "-created_at",
    )

    readonly_fields = (
        "created_at",
    )

    autocomplete_fields = (
        "user",
    )

    fieldsets = (
        (
            "User Information",
            {
                "fields": (
                    "user",
                    "type",
                )
            },
        ),
        (
            "Profile Details",
            {
                "fields": (
                    "file",
                    "description",
                )
            },
        ),
        (
            "Contact Information",
            {
                "fields": (
                    "location",
                    "tel",
                    "working_hours",
                )
            },
        ),
        (
            "Metadata",
            {
                "fields": (
                    "created_at",
                )
            },
        ),
    )

    def get_queryset(self, request):
        queryset = super().get_queryset(request)

        return queryset.select_related("user")