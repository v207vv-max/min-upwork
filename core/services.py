from django.db.models import Avg, Count

from bids.models import Bid, BidStatus
from contracts.models import Contract, ContractStatus
from projects.models import Project, ProjectStatus
from reviews.models import Review


def get_client_dashboard_data(user):
    """
    Build dashboard statistics for a client user.
    """

    projects = Project.objects.filter(client=user)
    contracts = Contract.objects.filter(client=user)
    written_reviews = Review.objects.filter(client=user)

    data = {
        "role": "client",
        "projects": {
            "total": projects.count(),
            "open": projects.filter(status=ProjectStatus.OPEN).count(),
            "in_progress": projects.filter(status=ProjectStatus.IN_PROGRESS).count(),
            "completed": projects.filter(status=ProjectStatus.COMPLETED).count(),
            "cancelled": projects.filter(status=ProjectStatus.CANCELLED).count(),
        },
        "contracts": {
            "total": contracts.count(),
            "active": contracts.filter(status=ContractStatus.ACTIVE).count(),
            "finished": contracts.filter(status=ContractStatus.FINISHED).count(),
            "cancelled": contracts.filter(status=ContractStatus.CANCELLED).count(),
        },
        "reviews": {
            "written": written_reviews.count(),
        },
        "recent_projects": projects.select_related("client")[:5],
        "recent_contracts": contracts.select_related(
            "project",
            "client",
            "freelancer",
        )[:5],
    }

    return data


def get_freelancer_dashboard_data(user):
    """
    Build dashboard statistics for a freelancer user.
    """

    bids = Bid.objects.filter(freelancer=user)
    contracts = Contract.objects.filter(freelancer=user)
    received_reviews = Review.objects.filter(freelancer=user)

    average_rating = received_reviews.aggregate(avg_rating=Avg("rating"))["avg_rating"]

    data = {
        "role": "freelancer",
        "bids": {
            "total": bids.count(),
            "pending": bids.filter(status=BidStatus.PENDING).count(),
            "accepted": bids.filter(status=BidStatus.ACCEPTED).count(),
            "rejected": bids.filter(status=BidStatus.REJECTED).count(),
            "withdrawn": bids.filter(status=BidStatus.WITHDRAWN).count(),
        },
        "contracts": {
            "total": contracts.count(),
            "active": contracts.filter(status=ContractStatus.ACTIVE).count(),
            "finished": contracts.filter(status=ContractStatus.FINISHED).count(),
            "cancelled": contracts.filter(status=ContractStatus.CANCELLED).count(),
        },
        "reviews": {
            "received": received_reviews.count(),
            "average_rating": round(average_rating, 2) if average_rating is not None else None,
        },
        "recent_bids": bids.select_related(
            "project",
            "freelancer",
            "project__client",
        )[:5],
        "recent_contracts": contracts.select_related(
            "project",
            "client",
            "freelancer",
        )[:5],
    }

    return data


def get_dashboard_data(user):
    """
    Return dashboard data based on user role.
    """

    if not user.is_authenticated:
        return None

    if getattr(user, "is_client", False):
        return get_client_dashboard_data(user)

    if getattr(user, "is_freelancer", False):
        return get_freelancer_dashboard_data(user)

    return {
        "role": None,
        "projects": {},
        "bids": {},
        "contracts": {},
        "reviews": {},
    }