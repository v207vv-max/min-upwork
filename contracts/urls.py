from django.urls import path

from .views import (
    contract_cancel_view,
    contract_detail_view,
    contract_finish_view,
    contract_list_view,
)

app_name = "contracts"

urlpatterns = [
    path("", contract_list_view, name="contract-list"),
    path("<int:pk>/", contract_detail_view, name="contract-detail"),
    path("<int:pk>/finish/", contract_finish_view, name="contract-finish"),
    path("<int:pk>/cancel/", contract_cancel_view, name="contract-cancel"),
]