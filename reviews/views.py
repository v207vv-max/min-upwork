from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied, ValidationError
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.translation import gettext_lazy as _

from contracts.models import Contract, ContractStatus

from .forms import ReviewCreateForm, ReviewUpdateForm
from .models import Review, ReviewSentiment
from .services import create_review, update_review


@login_required
def review_create_view(request, contract_id):
    if not request.user.is_client:
        raise PermissionDenied(_("Only clients can create reviews."))

    contract = get_object_or_404(
        Contract.objects.select_related(
            "project",
            "client",
            "freelancer",
        ),
        pk=contract_id,
        client=request.user,
    )

    if contract.status != ContractStatus.FINISHED:
        messages.error(request, _("You can leave a review only for a finished contract."))
        return redirect("contracts:contract-detail", pk=contract.pk)

    if hasattr(contract, "review"):
        messages.error(request, _("Review for this contract already exists."))
        return redirect("reviews:review-detail", pk=contract.review.pk)

    form = ReviewCreateForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        try:
            review = create_review(
                contract=contract,
                client=request.user,
                rating=form.cleaned_data["rating"],
                comment=form.cleaned_data["comment"],
            )
            messages.success(request, _("Review created successfully."))
            return redirect("reviews:review-detail", pk=review.pk)

        except ValidationError as e:
            form.add_error(None, str(e))

    return render(
        request,
        "reviews/review_create.html",
        {
            "form": form,
            "contract": contract,
        },
    )


@login_required
def review_update_view(request, pk):
    if not request.user.is_client:
        raise PermissionDenied(_("Only clients can update reviews."))

    review = get_object_or_404(
        Review.objects.select_related(
            "contract",
            "project",
            "client",
            "freelancer",
        ),
        pk=pk,
        client=request.user,
    )

    form = ReviewUpdateForm(request.POST or None, instance=review)

    if request.method == "POST" and form.is_valid():
        try:
            update_review(
                review=review,
                client=request.user,
                rating=form.cleaned_data["rating"],
                comment=form.cleaned_data["comment"],
            )
            messages.success(request, _("Review updated successfully."))
            return redirect("reviews:review-detail", pk=review.pk)

        except ValidationError as e:
            form.add_error(None, str(e))

    return render(
        request,
        "reviews/review_update.html",
        {
            "form": form,
            "review": review,
        },
    )


def review_detail_view(request, pk):
    review = get_object_or_404(
        Review.objects.select_related(
            "contract",
            "project",
            "client",
            "freelancer",
        ),
        pk=pk,
    )

    return render(
        request,
        "reviews/review_detail.html",
        {"review": review},
    )


@login_required
def written_reviews_view(request):
    if not request.user.is_client:
        raise PermissionDenied(_("Only clients can view written reviews."))

    reviews = Review.objects.select_related(
        "contract",
        "project",
        "client",
        "freelancer",
    ).filter(client=request.user)

    return render(
        request,
        "reviews/written_reviews.html",
        {"reviews": reviews},
    )


@login_required
def received_reviews_view(request):
    if not request.user.is_freelancer:
        raise PermissionDenied(_("Only freelancers can view received reviews."))

    reviews = Review.objects.select_related(
        "contract",
        "project",
        "client",
        "freelancer",
    ).filter(freelancer=request.user)

    rating = (request.GET.get("rating") or "").strip()
    sentiment = (request.GET.get("sentiment") or "").strip()
    ordering = (request.GET.get("ordering") or "").strip()

    if rating.isdigit():
        reviews = reviews.filter(rating=int(rating))

    valid_sentiments = {choice[0] for choice in ReviewSentiment.choices}
    if sentiment in valid_sentiments:
        if sentiment == ReviewSentiment.POSITIVE:
            reviews = reviews.filter(rating__gte=4)
        elif sentiment == ReviewSentiment.NEUTRAL:
            reviews = reviews.filter(rating=3)
        elif sentiment == ReviewSentiment.NEGATIVE:
            reviews = reviews.filter(rating__lte=2)

    ordering_map = {
        "newest": "-created_at",
        "oldest": "created_at",
        "rating_asc": "rating",
        "rating_desc": "-rating",
    }
    reviews = reviews.order_by(ordering_map.get(ordering, "-created_at"))

    return render(
        request,
        "reviews/received_reviews.html",
        {
            "reviews": reviews,
            "filters": request.GET,
            "review_sentiments": ReviewSentiment.choices,
        },
    )
