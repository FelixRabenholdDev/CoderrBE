"""
Serializers for offers and offer details.
"""

from rest_framework import serializers

from offers_app.models import Offer, OfferDetail


class OfferDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for offer detail objects.
    """

    offer_type = serializers.ChoiceField(
        choices=["basic", "standard", "premium"],
        required=True,
    )

    class Meta:
        """
        Meta configuration for OfferDetailSerializer.
        """

        model = OfferDetail

        fields = [
            "id",
            "title",
            "revisions",
            "delivery_time_in_days",
            "price",
            "features",
            "offer_type",
        ]


class OfferDetailUrlSerializer(serializers.ModelSerializer):
    """
    Serializer for offer detail URLs.
    """

    url = serializers.SerializerMethodField()

    class Meta:
        """
        Meta configuration for OfferDetailUrlSerializer.
        """

        model = OfferDetail
        fields = ["id", "url"]

    def get_url(self, obj):
        """
        Generate the absolute URL for an offer detail.

        Args:
            obj: OfferDetail instance.

        Returns:
            str: Absolute or relative URL.
        """

        request = self.context.get("request")
        url = f"/api/offerdetails/{obj.pk}/"

        if request:
            return request.build_absolute_uri(url)

        return url


class OfferListSerializer(serializers.ModelSerializer):
    """
    Serializer for listing offers.
    """

    details = OfferDetailUrlSerializer(
        many=True,
        read_only=True,
    )

    min_price = serializers.SerializerMethodField()

    min_delivery_time = serializers.SerializerMethodField()

    user_details = serializers.SerializerMethodField()

    class Meta:
        """
        Meta configuration for OfferListSerializer.
        """

        model = Offer

        fields = [
            "id",
            "user",
            "title",
            "image",
            "description",
            "created_at",
            "updated_at",
            "details",
            "min_price",
            "min_delivery_time",
            "user_details",
        ]

    def get_min_price(self, obj):
        """
        Get the minimum price of all offer details.

        Args:
            obj: Offer instance.

        Returns:
            Decimal | None:
                Lowest available price.
        """

        prices = obj.details.values_list(
            "price",
            flat=True,
        )

        return min(prices) if prices else None

    def get_min_delivery_time(self, obj):
        """
        Get the minimum delivery time of all offer details.

        Args:
            obj: Offer instance.

        Returns:
            int | None:
                Shortest delivery time.
        """

        times = obj.details.values_list(
            "delivery_time_in_days",
            flat=True,
        )

        return min(times) if times else None

    def get_user_details(self, obj):
        """
        Get basic user information.

        Args:
            obj: Offer instance.

        Returns:
            dict: User information dictionary.
        """

        return {
            "first_name": obj.user.first_name or "",
            "last_name": obj.user.last_name or "",
            "username": obj.user.username,
        }


class OfferCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating offers.
    """

    details = OfferDetailSerializer(many=True)

    class Meta:
        """
        Meta configuration for OfferCreateSerializer.
        """

        model = Offer
        fields = ["id", "title", "image", "description", "details"]

    def validate_details(self, value):
        """
        Validate the number of offer details.

        Args:
            value: List of offer details.

        Returns:
            list: Validated offer details.

        Raises:
            serializers.ValidationError:
                If the number of details is invalid.
        """

        if len(value) != 3:
            raise serializers.ValidationError(
                (
                    "Ein Angebot muss genau "
                    "3 Details enthalten."
                )
            )

        return value

    def create(self, validated_data):
        """
        Create an offer with related offer details.

        Args:
            validated_data (dict):
                Validated serializer data.

        Returns:
            Offer: Created offer instance.
        """

        details_data = validated_data.pop("details")

        offer = Offer.objects.create(**validated_data)

        for detail in details_data:
            OfferDetail.objects.create(
                offer=offer,
                **detail,
            )

        return offer


class OfferRetrieveSerializer(serializers.ModelSerializer):
    """
    Serializer for retrieving single offers.
    """

    details = OfferDetailUrlSerializer(
        many=True,
        read_only=True,
    )

    min_price = serializers.SerializerMethodField()

    min_delivery_time = serializers.SerializerMethodField()

    class Meta:
        """
        Meta configuration for OfferRetrieveSerializer.
        """

        model = Offer

        fields = [
            "id",
            "user",
            "title",
            "image",
            "description",
            "created_at",
            "updated_at",
            "details",
            "min_price",
            "min_delivery_time",
        ]

    def get_min_price(self, obj):
        """
        Get the minimum price of all offer details.

        Args:
            obj: Offer instance.

        Returns:
            Decimal | None:
                Lowest available price.
        """

        prices = obj.details.values_list(
            "price",
            flat=True,
        )

        return min(prices) if prices else None

    def get_min_delivery_time(self, obj):
        """
        Get the minimum delivery time of all offer details.

        Args:
            obj: Offer instance.

        Returns:
            int | None:
                Shortest delivery time.
        """

        times = obj.details.values_list(
            "delivery_time_in_days",
            flat=True,
        )

        return min(times) if times else None


class OfferPatchSerializer(serializers.ModelSerializer):
    """
    Serializer for partially updating offers.
    """

    details = OfferDetailSerializer(
        many=True,
        required=False,
    )

    class Meta:
        """
        Meta configuration for OfferPatchSerializer.
        """

        model = Offer
        fields = ["id", "title", "image", "description", "details"]

    def validate_details(self, value):
        """
        Validate that each detail contains offer_type.

        Args:
            value: List of detail dicts.

        Returns:
            list: Validated details.

        Raises:
            serializers.ValidationError:
                If offer_type is missing.
        """
        for detail in value:
            if "offer_type" not in detail:
                raise serializers.ValidationError(
                    "offer_type ist erforderlich."
                )
        return value

    def update(self, instance, validated_data):
        """
        Update an existing offer and related details.

        Args:
            instance: Existing Offer instance.
            validated_data (dict):
                Validated serializer data.

        Returns:
            Offer: Updated offer instance.
        """

        details_data = validated_data.pop(
            "details",
            None,
        )

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()

        if details_data:
            for detail_data in details_data:
                offer_type = detail_data.get(
                    "offer_type"
                )

                OfferDetail.objects.filter(
                    offer=instance,
                    offer_type=offer_type,
                ).update(
                    **{
                        k: v
                        for k, v in detail_data.items()
                        if k != "offer_type"
                    }
                )

        return instance