from django.db import models
from django.contrib.auth.models import User

class Review(models.Model):
    business_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reviews_received")
    reviewer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reviews_given")
    rating = models.IntegerField()
    description = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("business_user", "reviewer")

    def __str__(self):
        return f"Review by {self.reviewer} for {self.business_user} - {self.rating}"