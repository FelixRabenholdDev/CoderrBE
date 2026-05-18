from django.contrib import admin
from .models import Offer, OfferDetail


class OfferDetailInline(admin.TabularInline):
    model = OfferDetail
    extra = 0

    fields = (
        "offer_type",
        "title",
        "price",
        "delivery_time_in_days",
        "revisions",
    )


@admin.register(Offer)
class OfferAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "title",
        "user",
        "created_at",
        "updated_at",
    )

    search_fields = (
        "title",
        "description",
        "user__username",
        "user__email",
    )

    list_filter = (
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
        "user",
    )

    inlines = [OfferDetailInline]


@admin.register(OfferDetail)
class OfferDetailAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "offer",
        "offer_type",
        "price",
        "delivery_time_in_days",
        "revisions",
    )

    list_filter = (
        "offer_type",
    )

    search_fields = (
        "offer__title",
        "title",
    )

    ordering = (
        "offer",
        "offer_type",
    )

    autocomplete_fields = (
        "offer",
    )