from django import forms
from django.core.exceptions import ValidationError

from .models import Bid


class BidCreateForm(forms.ModelForm):
    class Meta:
        model = Bid
        fields = (
            "proposal",
            "price",
            "delivery_time_days",
        )
        widgets = {
            "proposal": forms.Textarea(attrs={"rows": 6}),
        }

    def clean_proposal(self):
        proposal = self.cleaned_data["proposal"].strip()

        if not proposal:
            raise ValidationError("Proposal cannot be empty.")

        if len(proposal) < 20:
            raise ValidationError("Proposal must contain at least 20 characters.")

        return proposal

    def clean_price(self):
        price = self.cleaned_data["price"]

        if price is None:
            raise ValidationError("Price is required.")

        if price <= 0:
            raise ValidationError("Price must be greater than 0.")

        return price

    def clean_delivery_time_days(self):
        delivery_time_days = self.cleaned_data["delivery_time_days"]

        if delivery_time_days is None:
            raise ValidationError("Delivery time is required.")

        if delivery_time_days < 1:
            raise ValidationError("Delivery time must be at least 1 day.")

        return delivery_time_days

    def clean(self):
        cleaned_data = super().clean()
        proposal = cleaned_data.get("proposal")

        if proposal:
            cleaned_data["proposal"] = proposal.strip()

        return cleaned_data


class BidUpdateForm(forms.ModelForm):
    class Meta:
        model = Bid
        fields = (
            "proposal",
            "price",
            "delivery_time_days",
        )
        widgets = {
            "proposal": forms.Textarea(attrs={"rows": 6}),
        }

    def clean_proposal(self):
        proposal = self.cleaned_data["proposal"].strip()

        if not proposal:
            raise ValidationError("Proposal cannot be empty.")

        if len(proposal) < 20:
            raise ValidationError("Proposal must contain at least 20 characters.")

        return proposal

    def clean_price(self):
        price = self.cleaned_data["price"]

        if price is None:
            raise ValidationError("Price is required.")

        if price <= 0:
            raise ValidationError("Price must be greater than 0.")

        return price

    def clean_delivery_time_days(self):
        delivery_time_days = self.cleaned_data["delivery_time_days"]

        if delivery_time_days is None:
            raise ValidationError("Delivery time is required.")

        if delivery_time_days < 1:
            raise ValidationError("Delivery time must be at least 1 day.")

        return delivery_time_days

    def clean(self):
        cleaned_data = super().clean()
        proposal = cleaned_data.get("proposal")

        if proposal:
            cleaned_data["proposal"] = proposal.strip()

        return cleaned_data