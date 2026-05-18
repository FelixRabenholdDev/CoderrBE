from django.db.models import Q


def filter_offers(queryset, request):
    """
    Apply filters, search, and ordering to offers queryset.

    Args:
        queryset: Base offers queryset.
        request: Incoming HTTP request.

    Returns:
        Filtered and ordered queryset.
    """
    creator_id = request.query_params.get("creator_id")
    if creator_id:
        queryset = queryset.filter(user__id=creator_id)

    min_price = request.query_params.get("min_price")
    if min_price:
        queryset = queryset.filter(min_price__gte=min_price)

    max_delivery_time = request.query_params.get("max_delivery_time")
    if max_delivery_time:
        queryset = queryset.filter(min_delivery_time__lte=max_delivery_time)

    search = request.query_params.get("search")
    if search:
        queryset = queryset.filter(
            Q(title__icontains=search) | Q(description__icontains=search)
        )

    ordering = request.query_params.get("ordering")
    if ordering == "min_price":
        queryset = queryset.order_by("min_price")
    elif ordering == "updated_at":
        queryset = queryset.order_by("updated_at")

    return queryset