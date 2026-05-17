"""
Serializers for review management.
"""

from rest_framework import serializers

from reviews_app.models import Review


class ReviewSerializer(serializers.ModelSerializer):
    """
    Serializer for review objects.
    """

    class Meta:
        """
        Meta configuration for ReviewSerializer.
        """

        model = Review

        fields = [
            "id",
            "business_user",
            "reviewer",
            "rating",
            "description",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "reviewer",
            "created_at",
            "updated_at",
        ]


class ReviewPatchSerializer(serializers.ModelSerializer):
    """
    Serializer for updating reviews.
    """

    class Meta:
        """
        Meta configuration for ReviewPatchSerializer.
        """

        model = Review

        fields = [
            "rating",
            "description",
        ]