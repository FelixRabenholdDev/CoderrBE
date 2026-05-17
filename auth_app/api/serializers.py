from django.contrib.auth.models import User
from django.contrib.auth import authenticate

from rest_framework import serializers

from profiles_app.models import UserProfile


class RegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration.
    """

    password = serializers.CharField(write_only=True)
    repeated_password = serializers.CharField(write_only=True)
    type = serializers.ChoiceField(
        choices=["customer", "business"]
    )
    email = serializers.EmailField(required=True)

    class Meta:
        """
        Meta configuration for RegistrationSerializer.
        """

        model = User
        fields = [
            "username",
            "email",
            "password",
            "repeated_password",
            "type",
        ]

    def validate(self, data):
        """
        Validate that both password fields match.

        Args:
            data (dict): Incoming serializer data.

        Returns:
            dict: Validated serializer data.

        Raises:
            serializers.ValidationError:
                If passwords do not match.
        """

        if data["password"] != data["repeated_password"]:
            raise serializers.ValidationError(
                {
                    "repeated_password": (
                        "Passwörter stimmen nicht überein."
                    )
                }
            )

        return data

    def create(self, validated_data):
        """
        Create a new user and corresponding user profile.

        Args:
            validated_data (dict):
                Validated serializer data.

        Returns:
            User: Created user instance.
        """

        user_type = validated_data.pop("type")
        validated_data.pop("repeated_password")

        user = User.objects.create_user(
            username=validated_data["username"],
            email=validated_data["email"],
            password=validated_data["password"],
        )

        UserProfile.objects.create(
            user=user,
            type=user_type,
        )

        return user


class LoginSerializer(serializers.Serializer):
    """
    Serializer for user login.
    """

    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        """
        Validate user credentials.

        Args:
            data (dict): Login data.

        Returns:
            dict: Validated data including authenticated user.

        Raises:
            serializers.ValidationError:
                If authentication fails.
        """

        user = authenticate(
            username=data["username"],
            password=data["password"],
        )

        if not user:
            raise serializers.ValidationError(
                "Ungültige Anmeldedaten."
            )

        data["user"] = user

        return data