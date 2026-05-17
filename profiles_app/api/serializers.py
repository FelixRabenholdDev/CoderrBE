"""
Serializers for user profile management.
"""

from rest_framework import serializers

from profiles_app.models import UserProfile


class UserProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for complete user profile data.
    """

    user = serializers.IntegerField(
        source="user.id",
        read_only=True,
    )

    username = serializers.CharField(
        source="user.username",
        read_only=True,
    )

    email = serializers.EmailField(
        source="user.email",
        read_only=True,
    )

    first_name = serializers.SerializerMethodField()

    last_name = serializers.SerializerMethodField()

    first_name_input = serializers.CharField(
        write_only=True,
        required=False,
    )

    last_name_input = serializers.CharField(
        write_only=True,
        required=False,
    )

    class Meta:
        """
        Meta configuration for UserProfileSerializer.
        """

        model = UserProfile

        fields = [
            "user",
            "username",
            "first_name",
            "first_name_input",
            "last_name",
            "last_name_input",
            "file",
            "location",
            "tel",
            "description",
            "working_hours",
            "type",
            "email",
            "created_at",
        ]

    def get_first_name(self, obj):
        """
        Return the user's first name.

        Args:
            obj: UserProfile instance.

        Returns:
            str: First name or empty string.
        """

        return obj.user.first_name or ""

    def get_last_name(self, obj):
        """
        Return the user's last name.

        Args:
            obj: UserProfile instance.

        Returns:
            str: Last name or empty string.
        """

        return obj.user.last_name or ""

    def update(self, instance, validated_data):
        """
        Update user profile and related user data.

        Args:
            instance: Existing UserProfile instance.
            validated_data (dict):
                Validated serializer data.

        Returns:
            UserProfile:
                Updated profile instance.
        """

        user_data = validated_data.pop(
            "user",
            {},
        )

        email = user_data.get("email")

        first_name = validated_data.pop(
            "first_name_input",
            None,
        )

        last_name = validated_data.pop(
            "last_name_input",
            None,
        )

        user = instance.user

        if email:
            user.email = email

        if first_name is not None:
            user.first_name = first_name

        if last_name is not None:
            user.last_name = last_name

        user.save()

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()

        return instance


class BusinessProfileSerializer(
    serializers.ModelSerializer
):
    """
    Serializer for business user profiles.
    """

    user = serializers.IntegerField(
        source="user.id",
        read_only=True,
    )

    username = serializers.CharField(
        source="user.username",
        read_only=True,
    )

    first_name = serializers.SerializerMethodField()

    last_name = serializers.SerializerMethodField()

    class Meta:
        """
        Meta configuration for
        BusinessProfileSerializer.
        """

        model = UserProfile

        fields = [
            "user",
            "username",
            "first_name",
            "last_name",
            "file",
            "location",
            "tel",
            "description",
            "working_hours",
            "type",
        ]

    def get_first_name(self, obj):
        """
        Return the user's first name.

        Args:
            obj: UserProfile instance.

        Returns:
            str: First name or empty string.
        """

        return obj.user.first_name or ""

    def get_last_name(self, obj):
        """
        Return the user's last name.

        Args:
            obj: UserProfile instance.

        Returns:
            str: Last name or empty string.
        """

        return obj.user.last_name or ""


class CustomerProfileSerializer(
    serializers.ModelSerializer
):
    """
    Serializer for customer user profiles.
    """

    user = serializers.IntegerField(
        source="user.id",
        read_only=True,
    )

    username = serializers.CharField(
        source="user.username",
        read_only=True,
    )

    first_name = serializers.SerializerMethodField()

    last_name = serializers.SerializerMethodField()

    uploaded_at = serializers.DateTimeField(
        source="created_at",
        read_only=True,
    )

    class Meta:
        """
        Meta configuration for
        CustomerProfileSerializer.
        """

        model = UserProfile

        fields = [
            "user",
            "username",
            "first_name",
            "last_name",
            "file",
            "uploaded_at",
            "type",
        ]

    def get_first_name(self, obj):
        """
        Return the user's first name.

        Args:
            obj: UserProfile instance.

        Returns:
            str: First name or empty string.
        """

        return obj.user.first_name or ""

    def get_last_name(self, obj):
        """
        Return the user's last name.

        Args:
            obj: UserProfile instance.

        Returns:
            str: Last name or empty string.
        """

        return obj.user.last_name or ""