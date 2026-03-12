from django.urls import path

from .views import (
    bid_accept_view,
    bid_create_view,
    bid_detail_view,
    bid_reject_view,
    bid_update_view,
    bid_withdraw_view,
    my_bids_view,
    project_bids_view,
)

app_name = "bids"

urlpatterns = [
    path("my/", my_bids_view, name="my-bids"),
    path("create/<int:project_id>/", bid_create_view, name="bid-create"),
    path("project/<int:project_id>/", project_bids_view, name="project-bids"),
    path("<int:pk>/", bid_detail_view, name="bid-detail"),
    path("<int:pk>/update/", bid_update_view, name="bid-update"),
    path("<int:pk>/withdraw/", bid_withdraw_view, name="bid-withdraw"),
    path("<int:pk>/accept/", bid_accept_view, name="bid-accept"),
    path("<int:pk>/reject/", bid_reject_view, name="bid-reject"),
]