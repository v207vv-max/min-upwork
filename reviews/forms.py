from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from .models import Review


class ReviewCreateForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = (
            "rating",
            "comment",
        )
        widgets = {
            "comment": forms.Textarea(attrs={"rows": 5}),
        }

    def clean_rating(self):
        rating = self.cleaned_data["rating"]

        if rating is None:
            raise ValidationError(_("Rating is required."))

        if rating < 1 or rating > 5:
            raise ValidationError(_("Rating must be between 1 and 5."))

        return rating

    def clean_comment(self):
        comment = self.cleaned_data["comment"].strip()

        if not comment:
            raise ValidationError(_("Comment cannot be empty."))

        if len(comment) < 10:
            raise ValidationError(_("Comment must contain at least 10 characters."))

        return comment

    def clean(self):
        cleaned_data = super().clean()
        comment = cleaned_data.get("comment")

        if comment:
            cleaned_data["comment"] = comment.strip()

        return cleaned_data


class ReviewUpdateForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = (
            "rating",
            "comment",
        )
        widgets = {
            "comment": forms.Textarea(attrs={"rows": 5}),
        }

    def clean_rating(self):
        rating = self.cleaned_data["rating"]

        if rating is None:
            raise ValidationError(_("Rating is required."))

        if rating < 1 or rating > 5:
            raise ValidationError(_("Rating must be between 1 and 5."))

        return rating

    def clean_comment(self):
        comment = self.cleaned_data["comment"].strip()

        if not comment:
            raise ValidationError(_("Comment cannot be empty."))

        if len(comment) < 10:
            raise ValidationError(_("Comment must contain at least 10 characters."))

        return comment

    def clean(self):
        cleaned_data = super().clean()
        comment = cleaned_data.get("comment")

        if comment:
            cleaned_data["comment"] = comment.strip()

        return cleaned_data
