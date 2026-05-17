"""
Database model for user reviews.
"""

from django.contrib.auth.models import User
from django.db import models


class Review(models.Model):
    """
    Model representing a review from one user
    to a business user.
    """

    business_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="reviews_received",
    )

    reviewer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="reviews_given",
    )

    rating = models.IntegerField()

    description = models.TextField(
        blank=True,
        default="",
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        """
        Meta configuration for Review model.
        """

        unique_together = (
            "business_user",
            "reviewer",
        )

    def __str__(self):
        """
        Return string representation of the review.

        Returns:
            str: Human-readable review summary.
        """

        return (
            f"Review by {self.reviewer} "
            f"for {self.business_user} - "
            f"{self.rating}"
        )