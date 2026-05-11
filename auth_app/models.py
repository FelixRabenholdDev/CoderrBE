from django.contrib.auth.models import User
from django.db import models

class UserProfile(models.Model):
    USER_TYPES = [("customer", "Customer"), ("business", "Business")]
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    type = models.CharField(max_length=20, choices=USER_TYPES)