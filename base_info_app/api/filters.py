"""
Database query helper functions for base info statistics.
"""

from django.db.models import Avg

from offers_app.models import Offer
from profiles_app.models import UserProfile
from reviews_app.models import Review


def get_review_count():
    return Review.objects.count()


def get_average_rating():
    average_rating = Review.objects.aggregate(
        avg=Avg("rating")
    )["avg"]

    return (
        round(average_rating, 1)
        if average_rating is not None
        else 0.0
    )


def get_business_profile_count():
    return UserProfile.objects.filter(
        type="business"
    ).count()


def get_offer_count():
    return Offer.objects.count()