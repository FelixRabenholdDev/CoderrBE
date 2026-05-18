"""
Database filter and query helper functions
for orders.
"""

from django.contrib.auth.models import User
from django.db.models import Q

from offers_app.models import OfferDetail
from orders_app.models import Order


def get_user_orders(user):
    """
    Return all orders related to a user.
    """

    return Order.objects.filter(
        Q(customer_user=user)
        | Q(business_user=user)
    ).order_by("created_at")


def get_offer_detail_by_pk(pk):
    """
    Return offer detail by primary key.
    """

    return OfferDetail.objects.get(pk=pk)


def get_order_by_pk(pk):
    """
    Return order by primary key.
    """

    return Order.objects.get(pk=pk)


def get_business_user_by_pk(pk):
    """
    Return business user by primary key.
    """

    return User.objects.get(pk=pk)


def get_in_progress_order_count(
    business_user,
):
    """
    Return count of active orders.
    """

    return Order.objects.filter(
        business_user=business_user,
        status="in_progress",
    ).count()


def get_completed_order_count(
    business_user,
):
    """
    Return count of completed orders.
    """

    return Order.objects.filter(
        business_user=business_user,
        status="completed",
    ).count()