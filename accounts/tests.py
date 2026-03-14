from datetime import timedelta

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from bids.models import BidStatus
from bids.services import create_bid
from contracts.models import Contract, ContractStatus
from projects.models import Project
from reviews.services import create_review

from .models import User, UserRole


class FreelancerProfileViewTests(TestCase):
    def setUp(self):
        self.client_user = User.objects.create_user(
            username="client1",
            password="testpass123",
            email="client@example.com",
            role=UserRole.CLIENT,
            is_active=True,
        )
        self.freelancer = User.objects.create_user(
            username="freelancer1",
            password="testpass123",
            email="freelancer@example.com",
            role=UserRole.FREELANCER,
            is_active=True,
        )

    def test_freelancer_profile_shows_rating_and_completed_orders(self):
        project = Project.objects.create(
            client=self.client_user,
            title="Landing page",
            description="Need a landing page for a campaign",
            budget=500,
            deadline=timezone.localdate() + timedelta(days=10),
        )
        bid = create_bid(
            project=project,
            freelancer=self.freelancer,
            proposal="I can complete this project with Django templates.",
            price=450,
            delivery_time_days=5,
        )
        bid.status = BidStatus.ACCEPTED
        bid.save(update_fields=["status", "updated_at"])
        contract = Contract.objects.create(
            project=project,
            bid=bid,
            client=self.client_user,
            freelancer=self.freelancer,
            agreed_price=bid.price,
            status=ContractStatus.FINISHED,
            started_at=timezone.now(),
            finished_at=timezone.now(),
        )
        create_review(
            contract=contract,
            client=self.client_user,
            rating=4,
            comment="Solid delivery, clean work and good communication.",
        )

        self.client.force_login(self.client_user)
        response = self.client.get(
            reverse("accounts:freelancer-profile", kwargs={"pk": self.freelancer.pk})
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["freelancer"], self.freelancer)
        self.assertEqual(response.context["freelancer_stats"]["average_rating"], 4.0)
        self.assertEqual(response.context["freelancer_stats"]["completed_orders"], 1)
        self.assertContains(response, "Completed orders")

    def test_client_profile_is_not_available_via_freelancer_route(self):
        self.client.force_login(self.client_user)

        response = self.client.get(
            reverse("accounts:freelancer-profile", kwargs={"pk": self.client_user.pk})
        )

        self.assertEqual(response.status_code, 404)
