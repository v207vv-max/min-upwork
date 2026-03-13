from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied, ValidationError
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.translation import gettext_lazy as _
from .services import cancel_contract, finish_contract
from .models import Contract, ContractStatus

@login_required
def contract_list_view(request):
    if request.user.is_client:
        contracts = Contract.objects.select_related(
            "project",
            "bid",
            "client",
            "freelancer",
        ).filter(client=request.user)

    elif request.user.is_freelancer:
        contracts = Contract.objects.select_related(
            "project",
            "bid",
            "client",
            "freelancer",
        ).filter(freelancer=request.user)

    else:
        raise PermissionDenied(_("You do not have permission to view contracts."))

    status = (request.GET.get("status") or "").strip()
    ordering = (request.GET.get("ordering") or "").strip()

    valid_statuses = {choice[0] for choice in ContractStatus.choices}
    if status in valid_statuses:
        contracts = contracts.filter(status=status)

    ordering_map = {
        "newest": "-created_at",
        "oldest": "created_at",
        "started_asc": "started_at",
        "started_desc": "-started_at",
    }
    contracts = contracts.order_by(ordering_map.get(ordering, "-created_at"))

    return render(
        request,
        "contracts/contract_list.html",
        {
            "contracts": contracts,
            "filters": request.GET,
            "contract_statuses": ContractStatus.choices,
        },
    )

@login_required
def contract_detail_view(request, pk):
    contract = get_object_or_404(
        Contract.objects.select_related(
            "project",
            "bid",
            "client",
            "freelancer",
        ),
        pk=pk,
    )

    is_client_owner = contract.client == request.user
    is_freelancer_owner = contract.freelancer == request.user

    if not (is_client_owner or is_freelancer_owner):
        raise PermissionDenied(_("You do not have permission to view this contract."))

    return render(
        request,
        "contracts/contract_detail.html",
        {"contract": contract},
    )


@login_required
def contract_finish_view(request, pk):
    if not request.user.is_client:
        raise PermissionDenied(_("Only clients can finish contracts."))

    contract = get_object_or_404(
        Contract.objects.select_related(
            "project",
            "bid",
            "client",
            "freelancer",
        ),
        pk=pk,
        client=request.user,
    )

    if request.method == "POST":
        try:
            finish_contract(
                contract=contract,
                client=request.user,
            )
            messages.success(request, _("Contract finished successfully."))
            return redirect("contracts:contract-detail", pk=contract.pk)

        except ValidationError as e:
            messages.error(request, str(e))
            return redirect("contracts:contract-detail", pk=contract.pk)

    return render(
        request,
        "contracts/contract_finish.html",
        {"contract": contract},
    )


@login_required
def contract_cancel_view(request, pk):
    if not request.user.is_client:
        raise PermissionDenied(_("Only clients can cancel contracts."))

    contract = get_object_or_404(
        Contract.objects.select_related(
            "project",
            "bid",
            "client",
            "freelancer",
        ),
        pk=pk,
        client=request.user,
    )

    if request.method == "POST":
        try:
            cancel_contract(
                contract=contract,
                client=request.user,
            )
            messages.success(request, _("Contract cancelled successfully."))
            return redirect("contracts:contract-detail", pk=contract.pk)

        except ValidationError as e:
            messages.error(request, str(e))
            return redirect("contracts:contract-detail", pk=contract.pk)

    return render(
        request,
        "contracts/contract_cancel.html",
        {"contract": contract},
    )
