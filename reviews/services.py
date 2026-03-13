from django.core.exceptions import ValidationError
from django.db import transaction

from contracts.models import ContractStatus

from .models import Review


@transaction.atomic
def create_review(*, contract, client, rating, comment):
    """
    Create a review for a finished contract.
    """

    if contract.client != client:
        raise ValidationError("You can create a review only for your own contract.")

    if contract.status != ContractStatus.FINISHED:
        raise ValidationError("Review can only be created for a finished contract.")

    if hasattr(contract, "review"):
        raise ValidationError("Review for this contract already exists.")

    review = Review.objects.create(
        contract=contract,
        project=contract.project,
        client=contract.client,
        freelancer=contract.freelancer,
        rating=rating,
        comment=comment,
    )

    return review


@transaction.atomic
def update_review(*, review, client, rating, comment):
    """
    Update an existing review.
    """

    if review.client != client:
        raise ValidationError("You can update only your own review.")

    if review.contract.status != ContractStatus.FINISHED:
        raise ValidationError("You can update review only for a finished contract.")

    review.rating = rating
    review.comment = comment
    review.save()

    return review