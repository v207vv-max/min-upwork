from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from .services import get_dashboard_data


def home_view(request):
    if request.user.is_authenticated:
        return redirect("core:dashboard")

    return render(request, "core/home.html")


@login_required
def dashboard_view(request):
    dashboard_data = get_dashboard_data(request.user)

    return render(
        request,
        "core/dashboard.html",
        {
            "dashboard": dashboard_data,
        },
    )