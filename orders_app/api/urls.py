"""
URL configuration for order-related endpoints.
"""

from django.urls import path

from .views import (
    CompletedOrderCountView,
    OrderCountView,
    OrderDetailView,
    OrdersListView,
)


urlpatterns = [
    path(
        "orders/",
        OrdersListView.as_view(),
        name="orders-list",
    ),
    path(
        "orders/<int:pk>/",
        OrderDetailView.as_view(),
        name="order-detail",
    ),
    path(
        "order-count/<int:business_user_id>/",
        OrderCountView.as_view(),
        name="order-count",
    ),
    path(
        "completed-order-count/<int:business_user_id>/",
        CompletedOrderCountView.as_view(),
        name="completed-order-count",
    ),
]