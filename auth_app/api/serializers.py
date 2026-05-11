from django.contrib.auth.models import User
from rest_framework import serializers

from auth_app.models import UserProfile


class RegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    repeated_password = serializers.CharField(write_only=True)
    type = serializers.ChoiceField(choices=["customer", "business"])
    email = serializers.EmailField(required=True)
    
    class Meta:
        model = User
        fields = ["username", "email", "password", "repeated_password", "type"]

    def validate(self, data):
        if data["password"] != data["repeated_password"]:
            raise serializers.ValidationError({"repeated_password": "Passwörter stimmen nicht überein."})
        return data

    def create(self, validated_data):
        user_type = validated_data.pop("type")
        validated_data.pop("repeated_password")

        user = User.objects.create_user(
            username=validated_data["username"],
            email=validated_data["email"],
            password=validated_data["password"],
        )
        UserProfile.objects.create(user=user, type=user_type)
        return user