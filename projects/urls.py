from django.urls import path

from .views import (
    my_projects_view,
    project_cancel_view,
    project_complete_view,
    project_create_view,
    project_detail_view,
    project_list_view,
    project_update_view,
)

app_name = "projects"

urlpatterns = [
    path("", project_list_view, name="project-list"),
    path("my/", my_projects_view, name="my-projects"),
    path("create/", project_create_view, name="project-create"),
    path("<int:pk>/", project_detail_view, name="project-detail"),
    path("<int:pk>/update/", project_update_view, name="project-update"),
    path("<int:pk>/cancel/", project_cancel_view, name="project-cancel"),
    path("<int:pk>/complete/", project_complete_view, name="project-complete"),
]