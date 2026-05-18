def filter_reviews(queryset, request):
    business_user_id = request.query_params.get("business_user_id")
    if business_user_id:
        queryset = queryset.filter(business_user__id=business_user_id)

    reviewer_id = request.query_params.get("reviewer_id")
    if reviewer_id:
        queryset = queryset.filter(reviewer__id=reviewer_id)

    ordering = request.query_params.get("ordering")
    if ordering in ["rating", "updated_at"]:
        queryset = queryset.order_by(ordering)
    else:
        queryset = queryset.order_by("updated_at")

    return queryset