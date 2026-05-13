from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .serializers import UserProfileSerializer, BusinessProfileSerializer, CustomerProfileSerializer
from profiles_app.models import UserProfile

class ProfileDetailView(APIView):

    def get(self, request, pk):
        try:
            profile = UserProfile.objects.get(user__pk=pk)
        except UserProfile.DoesNotExist:
            return Response({"detail": "Nicht gefunden."}, status=status.HTTP_404_NOT_FOUND)

        serializer = UserProfileSerializer(profile)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, pk):
        try:
            profile = UserProfile.objects.get(user__pk=pk)
        except UserProfile.DoesNotExist:
            return Response({"detail": "Nicht gefunden."}, status=status.HTTP_404_NOT_FOUND)

        if profile.user != request.user:
            return Response({"detail": "Nicht erlaubt."}, status=status.HTTP_403_FORBIDDEN)

        user = profile.user
        if "first_name" in request.data:
            user.first_name = request.data["first_name"]
        if "last_name" in request.data:
            user.last_name = request.data["last_name"]
        if "email" in request.data:
            user.email = request.data["email"]
        user.save()

        serializer = UserProfileSerializer(profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class BusinessProfilesView(APIView):

    def get(self, request):
        profiles = UserProfile.objects.filter(type="business")
        serializer = BusinessProfileSerializer(profiles, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class CustomerProfilesView(APIView):

    def get(self, request):
        profiles = UserProfile.objects.filter(type="customer")
        serializer = CustomerProfileSerializer(profiles, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)