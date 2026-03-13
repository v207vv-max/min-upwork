from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from .models import Project


class ProjectCreateForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = (
            "title",
            "description",
            "budget",
            "deadline",
            "skills_required",
        )
        widgets = {
            "description": forms.Textarea(attrs={"rows": 5}),
            "deadline": forms.DateInput(attrs={"type": "date"}),
        }

    def clean_title(self):
        title = self.cleaned_data["title"].strip()
        if not title:
            raise ValidationError(_("Title cannot be empty."))
        return title

    def clean_budget(self):
        budget = self.cleaned_data["budget"]

        if budget is None:
            raise ValidationError(_("Budget is required."))
        if budget <= 0:
            raise ValidationError(_("Budget must be greater than 0."))

        return budget

    def clean_deadline(self):
        deadline = self.cleaned_data["deadline"]

        if deadline < timezone.localdate():
            raise ValidationError(_("Deadline cannot be in the past."))

        return deadline

    def clean_skills_required(self):
        skills_required = self.cleaned_data.get("skills_required", "")
        return skills_required.strip()

    def clean(self):
        cleaned_data = super().clean()
        title = cleaned_data.get("title")
        description = cleaned_data.get("description")

        if title and len(title) < 5:
            raise ValidationError(_("Title must contain at least 5 characters."))

        if description:
            description = description.strip()
            cleaned_data["description"] = description

            if len(description) < 20:
                raise ValidationError(_("Description must contain at least 20 characters."))

        return cleaned_data


class ProjectUpdateForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = (
            "title",
            "description",
            "budget",
            "deadline",
            "skills_required",
        )
        widgets = {
            "description": forms.Textarea(attrs={"rows": 5}),
            "deadline": forms.DateInput(attrs={"type": "date"}),
        }

    def clean_title(self):
        title = self.cleaned_data["title"].strip()
        if not title:
            raise ValidationError(_("Title cannot be empty."))
        return title

    def clean_budget(self):
        budget = self.cleaned_data["budget"]

        if budget is None:
            raise ValidationError(_("Budget is required."))
        if budget <= 0:
            raise ValidationError(_("Budget must be greater than 0."))

        return budget

    def clean_deadline(self):
        deadline = self.cleaned_data["deadline"]

        if deadline < timezone.localdate():
            raise ValidationError(_("Deadline cannot be in the past."))

        return deadline

    def clean_skills_required(self):
        skills_required = self.cleaned_data.get("skills_required", "")
        return skills_required.strip()

    def clean(self):
        cleaned_data = super().clean()
        title = cleaned_data.get("title")
        description = cleaned_data.get("description")

        if title and len(title) < 5:
            raise ValidationError(_("Title must contain at least 5 characters."))

        if description:
            description = description.strip()
            cleaned_data["description"] = description

            if len(description) < 20:
                raise ValidationError(_("Description must contain at least 20 characters."))

        return cleaned_data
