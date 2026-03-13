from django.shortcuts import redirect, render


from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from core.services import get_activity_chart_data, get_dashboard_data


def home_view(request):
    if request.user.is_authenticated:
        return redirect("core:dashboard")

    return render(request, "core/home.html")


@login_required
def dashboard_view(request):
    period = request.GET.get("period", "week")

    dashboard_data = get_dashboard_data(request.user)
    activity_chart = get_activity_chart_data(request.user, period=period)

    return render(
        request,
        "core/dashboard.html",
        {
            "dashboard": dashboard_data,
            "activity_chart": activity_chart,
            "selected_period": period,
        },
    )