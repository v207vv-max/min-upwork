from django.urls import path

from .views import conversation_detail_view, conversation_list_view

app_name = "chat"

urlpatterns = [
    path("", conversation_list_view, name="conversation-list"),
    path("<int:pk>/", conversation_detail_view, name="conversation-detail"),
]