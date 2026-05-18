"""
Database filter and query helper functions
for profiles.
"""

from profiles_app.models import UserProfile


def get_profile_by_user_pk(pk):
    """
    Return profile by user primary key.
    """

    return UserProfile.objects.get(user__pk=pk)


def get_business_profiles():
    """
    Return all business profiles.
    """

    return UserProfile.objects.filter(
        type="business"
    )


def get_customer_profiles():
    """
    Return all customer profiles.
    """

    return UserProfile.objects.filter(
        type="customer"
    )