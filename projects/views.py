from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.core.exceptions import PermissionDenied, ValidationError
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.translation import gettext_lazy as _

from .forms import ProjectCreateForm, ProjectUpdateForm
from .models import Project, ProjectStatus
from .services import filter_projects, get_project_list_queryset


def project_list_view(request):
    projects = get_project_list_queryset()
    projects = filter_projects(projects, request.GET)
    paginator = Paginator(projects, 6)
    page_obj = paginator.get_page(request.GET.get("page"))
    query_params = request.GET.copy()
    query_params.pop("page", None)

    return render(
        request,
        "projects/project_list.html",
        {
            "projects": page_obj,
            "page_obj": page_obj,
            "filters": request.GET,
            "project_statuses": ProjectStatus.choices,
            "query_string": query_params.urlencode(),
        },
    )


def project_detail_view(request, pk):
    project = get_object_or_404(
        Project.objects.select_related("client"),
        pk=pk,
    )

    return render(
        request,
        "projects/project_detail.html",
        {"project": project},
    )


@login_required
def my_projects_view(request):
    if not request.user.is_client:
        raise PermissionDenied(_("Only clients can view their projects."))

    projects = Project.objects.select_related("client").filter(client=request.user)
    projects = filter_projects(projects, request.GET)

    return render(
        request,
        "projects/my_projects.html",
        {
            "projects": projects,
            "filters": request.GET,
            "project_statuses": ProjectStatus.choices,
        },
    )


@login_required
def project_create_view(request):
    if not request.user.is_client:
        raise PermissionDenied(_("Only clients can create projects."))

    form = ProjectCreateForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        try:
            project = form.save(commit=False)
            project.client = request.user
            project.save()

            messages.success(request, _("Project created successfully."))
            return redirect("projects:project-detail", pk=project.pk)

        except ValidationError as e:
            form.add_error(None, str(e))

    return render(
        request,
        "projects/project_create.html",
        {"form": form},
    )


@login_required
def project_update_view(request, pk):
    if not request.user.is_client:
        raise PermissionDenied(_("Only clients can update projects."))

    project = get_object_or_404(
        Project.objects.select_related("client"),
        pk=pk,
        client=request.user,
    )

    if not project.is_editable:
        messages.error(request, _("Only open projects can be edited."))
        return redirect("projects:project-detail", pk=project.pk)

    form = ProjectUpdateForm(request.POST or None, instance=project)

    if request.method == "POST" and form.is_valid():
        try:
            project = form.save()
            messages.success(request, _("Project updated successfully."))
            return redirect("projects:project-detail", pk=project.pk)

        except ValidationError as e:
            form.add_error(None, str(e))

    return render(
        request,
        "projects/project_update.html",
        {
            "form": form,
            "project": project,
        },
    )


@login_required
def project_cancel_view(request, pk):
    if not request.user.is_client:
        raise PermissionDenied(_("Only clients can cancel projects."))

    project = get_object_or_404(
        Project.objects.select_related("client"),
        pk=pk,
        client=request.user,
    )

    if hasattr(project, "contract"):
        messages.error(
            request,
            _("This project already has a contract. Cancel it through the contract page.")
        )
        return redirect("projects:project-detail", pk=project.pk)

    if project.status == ProjectStatus.CANCELLED:
        messages.info(request, _("Project is already cancelled."))
        return redirect("projects:project-detail", pk=project.pk)

    if project.status == ProjectStatus.COMPLETED:
        messages.error(request, _("Completed project cannot be cancelled."))
        return redirect("projects:project-detail", pk=project.pk)

    if request.method == "POST":
        project.status = ProjectStatus.CANCELLED
        project.is_active = False
        project.save(update_fields=["status", "is_active", "updated_at"])

        messages.success(request, _("Project cancelled successfully."))
        return redirect("projects:project-detail", pk=project.pk)

    return render(
        request,
        "projects/project_cancel.html",
        {"project": project},
    )


@login_required
def project_complete_view(request, pk):
    if not request.user.is_client:
        raise PermissionDenied(_("Only clients can complete projects."))

    project = get_object_or_404(
        Project.objects.select_related("client"),
        pk=pk,
        client=request.user,
    )

    if hasattr(project, "contract"):
        messages.error(
            request,
            _("This project already has a contract. Finish it through the contract page.")
        )
        return redirect("projects:project-detail", pk=project.pk)

    if project.status == ProjectStatus.COMPLETED:
        messages.info(request, _("Project is already completed."))
        return redirect("projects:project-detail", pk=project.pk)

    if project.status == ProjectStatus.CANCELLED:
        messages.error(request, _("Cancelled project cannot be completed."))
        return redirect("projects:project-detail", pk=project.pk)

    if request.method == "POST":
        project.status = ProjectStatus.COMPLETED
        project.is_active = False
        project.save(update_fields=["status", "is_active", "updated_at"])

        messages.success(request, _("Project marked as completed."))
        return redirect("projects:project-detail", pk=project.pk)

    return render(
        request,
        "projects/project_complete.html",
        {"project": project},
    )
