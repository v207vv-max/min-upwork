from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from .models import Message


class MessageCreateForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = (
            "text",
            "image",
        )
        widgets = {
            "text": forms.Textarea(
                attrs={
                    "rows": 3,
                    "placeholder": "Write your message...",
                }
            ),
        }

    def clean_text(self):
        text = self.cleaned_data.get("text", "")

        if text:
            text = text.strip()

        return text

    def clean(self):
        cleaned_data = super().clean()
        text = cleaned_data.get("text")
        image = cleaned_data.get("image")

        if text:
            cleaned_data["text"] = text.strip()

        if not text and not image:
            raise ValidationError(_("Message must contain text or image."))

        if text and len(text) > 3000:
            raise ValidationError(_("Message text cannot be longer than 3000 characters."))

        return cleaned_data
