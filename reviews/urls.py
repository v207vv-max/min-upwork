from django.urls import path

from .views import (
    received_reviews_view,
    review_create_view,
    review_detail_view,
    review_update_view,
    written_reviews_view,
)

app_name = "reviews"

urlpatterns = [
    path("written/", written_reviews_view, name="written-reviews"),
    path("received/", received_reviews_view, name="received-reviews"),
    path("create/<int:contract_id>/", review_create_view, name="review-create"),
    path("<int:pk>/", review_detail_view, name="review-detail"),
    path("<int:pk>/update/", review_update_view, name="review-update"),
]