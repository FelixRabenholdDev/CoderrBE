"""
Views for user registration and authentication.
"""

from django.contrib.auth import authenticate

from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import LoginSerializer, RegistrationSerializer


class RegistrationView(APIView):
    """
    API view for user registration.
    """

    permission_classes = [AllowAny]

    def post(self, request):
        """
        Handle user registration requests.

        Args:
            request: Incoming HTTP request containing
                registration data.

        Returns:
            Response:
                HTTP response with token and user data
                or validation errors.
        """

        serializer = RegistrationSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.save()
            token, _ = Token.objects.get_or_create(user=user)

            return Response(
                {
                    "token": token.key,
                    "username": user.username,
                    "email": user.email,
                    "user_id": user.id,
                },
                status=status.HTTP_201_CREATED,
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )


class LoginView(APIView):
    """
    API view for user login.
    """

    permission_classes = [AllowAny]

    def post(self, request):
        """
        Handle user login requests.

        Args:
            request: Incoming HTTP request containing
                login credentials.

        Returns:
            Response:
                HTTP response with token and user data
                or validation errors.
        """

        serializer = LoginSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.validated_data["user"]
            token, _ = Token.objects.get_or_create(user=user)

            return Response(
                {
                    "token": token.key,
                    "username": user.username,
                    "email": user.email,
                    "user_id": user.id,
                },
                status=status.HTTP_200_OK,
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )