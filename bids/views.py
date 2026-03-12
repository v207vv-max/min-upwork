from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied, ValidationError
from django.shortcuts import get_object_or_404, redirect, render

from projects.models import Project, ProjectStatus

from .forms import BidCreateForm, BidUpdateForm
from .models import Bid, BidStatus
from .services import accept_bid, create_bid, reject_bid, update_bid, withdraw_bid


@login_required
def bid_create_view(request, project_id):
    if not request.user.is_freelancer:
        raise PermissionDenied("Only freelancers can create bids.")

    project = get_object_or_404(
        Project.objects.select_related("client"),
        pk=project_id,
    )

    form = BidCreateForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        try:
            bid = create_bid(
                project=project,
                freelancer=request.user,
                proposal=form.cleaned_data["proposal"],
                price=form.cleaned_data["price"],
                delivery_time_days=form.cleaned_data["delivery_time_days"],
            )
            messages.success(request, "Bid submitted successfully.")
            return redirect("bids:my-bids")

        except ValidationError as e:
            form.add_error(None, str(e))

    return render(
        request,
        "bids/bid_create.html",
        {
            "form": form,
            "project": project,
        },
    )


@login_required
def my_bids_view(request):
    if not request.user.is_freelancer:
        raise PermissionDenied("Only freelancers can view their bids.")

    bids = Bid.objects.select_related("project", "project__client").filter(
        freelancer=request.user,
    )

    return render(
        request,
        "bids/my_bids.html",
        {"bids": bids},
    )


@login_required
def bid_update_view(request, pk):
    if not request.user.is_freelancer:
        raise PermissionDenied("Only freelancers can update bids.")

    bid = get_object_or_404(
        Bid.objects.select_related("project", "project__client", "freelancer"),
        pk=pk,
        freelancer=request.user,
    )

    if not bid.is_editable:
        messages.error(request, "Only pending bids can be updated.")
        return redirect("bids:my-bids")

    form = BidUpdateForm(request.POST or None, instance=bid)

    if request.method == "POST" and form.is_valid():
        try:
            update_bid(
                bid=bid,
                freelancer=request.user,
                proposal=form.cleaned_data["proposal"],
                price=form.cleaned_data["price"],
                delivery_time_days=form.cleaned_data["delivery_time_days"],
            )
            messages.success(request, "Bid updated successfully.")
            return redirect("bids:my-bids")

        except ValidationError as e:
            form.add_error(None, str(e))

    return render(
        request,
        "bids/bid_update.html",
        {
            "form": form,
            "bid": bid,
        },
    )


@login_required
def bid_withdraw_view(request, pk):
    if not request.user.is_freelancer:
        raise PermissionDenied("Only freelancers can withdraw bids.")

    bid = get_object_or_404(
        Bid.objects.select_related("project", "project__client", "freelancer"),
        pk=pk,
        freelancer=request.user,
    )

    if not bid.can_be_withdrawn:
        messages.error(request, "Only pending bids can be withdrawn.")
        return redirect("bids:my-bids")

    if request.method == "POST":
        try:
            withdraw_bid(
                bid=bid,
                freelancer=request.user,
            )
            messages.success(request, "Bid withdrawn successfully.")
            return redirect("bids:my-bids")

        except ValidationError as e:
            messages.error(request, str(e))
            return redirect("bids:my-bids")

    return render(
        request,
        "bids/bid_withdraw.html",
        {"bid": bid},
    )


@login_required
def project_bids_view(request, project_id):
    if not request.user.is_client:
        raise PermissionDenied("Only clients can view project bids.")

    project = get_object_or_404(
        Project.objects.select_related("client"),
        pk=project_id,
        client=request.user,
    )

    bids = project.bids.select_related("freelancer").all()

    return render(
        request,
        "bids/project_bids.html",
        {
            "project": project,
            "bids": bids,
        },
    )


@login_required
def bid_detail_view(request, pk):
    bid = get_object_or_404(
        Bid.objects.select_related("project", "project__client", "freelancer"),
        pk=pk,
    )

    is_freelancer_owner = request.user.is_authenticated and bid.freelancer == request.user
    is_project_client = request.user.is_authenticated and bid.project.client == request.user

    if not (is_freelancer_owner or is_project_client):
        raise PermissionDenied("You do not have permission to view this bid.")

    return render(
        request,
        "bids/bid_detail.html",
        {"bid": bid},
    )


@login_required
def bid_accept_view(request, pk):
    if not request.user.is_client:
        raise PermissionDenied("Only clients can accept bids.")

    bid = get_object_or_404(
        Bid.objects.select_related("project", "project__client", "freelancer"),
        pk=pk,
    )

    if bid.project.client != request.user:
        raise PermissionDenied("You can accept bids only for your own projects.")

    if bid.project.status != ProjectStatus.OPEN:
        messages.error(request, "Only bids for open projects can be accepted.")
        return redirect("bids:project-bids", project_id=bid.project.pk)

    if bid.status != BidStatus.PENDING:
        messages.error(request, "Only pending bids can be accepted.")
        return redirect("bids:project-bids", project_id=bid.project.pk)

    if request.method == "POST":
        try:
            accept_bid(
                bid=bid,
                client=request.user,
            )
            messages.success(request, "Bid accepted successfully.")
            return redirect("bids:project-bids", project_id=bid.project.pk)

        except ValidationError as e:
            messages.error(request, str(e))
            return redirect("bids:project-bids", project_id=bid.project.pk)

    return render(
        request,
        "bids/bid_accept.html",
        {"bid": bid},
    )


@login_required
def bid_reject_view(request, pk):
    if not request.user.is_client:
        raise PermissionDenied("Only clients can reject bids.")

    bid = get_object_or_404(
        Bid.objects.select_related("project", "project__client", "freelancer"),
        pk=pk,
    )

    if bid.project.client != request.user:
        raise PermissionDenied("You can reject bids only for your own projects.")

    if bid.status != BidStatus.PENDING:
        messages.error(request, "Only pending bids can be rejected.")
        return redirect("bids:project-bids", project_id=bid.project.pk)

    if request.method == "POST":
        try:
            reject_bid(
                bid=bid,
                client=request.user,
            )
            messages.success(request, "Bid rejected successfully.")
            return redirect("bids:project-bids", project_id=bid.project.pk)

        except ValidationError as e:
            messages.error(request, str(e))
            return redirect("bids:project-bids", project_id=bid.project.pk)

    return render(
        request,
        "bids/bid_reject.html",
        {"bid": bid},
    )