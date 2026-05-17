"""
Database model for orders.
"""

from django.contrib.auth.models import User
from django.db import models


class Order(models.Model):
    """
    Model representing an order between
    a customer and a business user.
    """

    STATUS_CHOICES = [
        ("in_progress", "In Progress"),
        ("completed", "Completed"),
        ("cancelled", "Cancelled"),
    ]

    customer_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="orders_as_customer",
    )

    business_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="orders_as_business",
    )

    title = models.CharField(max_length=255)

    revisions = models.IntegerField()

    delivery_time_in_days = models.IntegerField()

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
    )

    features = models.JSONField(default=list)

    offer_type = models.CharField(max_length=20)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="in_progress",
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        """
        Return the string representation
        of the order.

        Returns:
            str: Order identifier and title.
        """

        return f"Order {self.id} - {self.title}"