from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from .models import User, UserRole, VerificationChannel


class SignUpForm(forms.Form):
    username = forms.CharField(max_length=150)
    role = forms.ChoiceField(choices=UserRole.choices)
    email = forms.EmailField(required=False)
    phone_number = forms.CharField(max_length=20, required=False)
    preferred_contact_method = forms.ChoiceField(
        choices=VerificationChannel.choices,
        required=False,
    )
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["preferred_contact_method"].choices = [("", _("---------")), *VerificationChannel.choices]
        self.fields["email"].required = False
        self.fields["phone_number"].required = False
        self.fields["preferred_contact_method"].required = False
        self.fields["email"].widget.attrs["required"] = False
        self.fields["phone_number"].widget.attrs["required"] = False
        self.fields["preferred_contact_method"].widget.attrs["required"] = False

    def clean_username(self):
        username = self.cleaned_data["username"].strip()
        if User.objects.filter(username=username).exists():
            raise ValidationError(_("Username already exists."))
        return username

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if email:
            email = email.strip().lower()
            if User.objects.filter(email=email).exists():
                raise ValidationError(_("Email already exists."))
        return email

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get("phone_number")
        if phone_number:
            phone_number = "".join(phone_number.strip().split())
            if User.objects.filter(phone_number=phone_number).exists():
                raise ValidationError(_("Phone number already exists."))
        return phone_number

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get("email")
        phone_number = cleaned_data.get("phone_number")
        preferred_contact_method = cleaned_data.get("preferred_contact_method")
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if not email and not phone_number:
            raise ValidationError(_("You must provide either email or phone number."))

        if password and confirm_password and password != confirm_password:
            raise ValidationError(_("Passwords do not match."))

        if preferred_contact_method == VerificationChannel.EMAIL and not email:
            raise ValidationError(_("Preferred contact method is email, but email is empty."))

        if preferred_contact_method == VerificationChannel.PHONE and not phone_number:
            raise ValidationError(_("Preferred contact method is phone, but phone number is empty."))

        return cleaned_data


class VerifyCodeForm(forms.Form):
    code = forms.CharField(max_length=10)

    def clean_code(self):
        code = self.cleaned_data["code"].strip()
        if not code:
            raise ValidationError(_("Code is required."))
        return code


class LoginForm(forms.Form):
    identifier = forms.CharField(
        max_length=255,
        help_text=_("Username, email or phone number"),
    )
    password = forms.CharField(widget=forms.PasswordInput)

    def clean_identifier(self):
        return self.cleaned_data["identifier"].strip()


class ForgotPasswordForm(forms.Form):
    identifier = forms.CharField(
        max_length=255,
        help_text=_("Username, email or phone number"),
    )

    def clean_identifier(self):
        identifier = self.cleaned_data["identifier"].strip()
        if not identifier:
            raise ValidationError(_("Identifier is required."))
        return identifier


class ResetPasswordForm(forms.Form):
    code = forms.CharField(max_length=10)
    new_password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)

    def clean_code(self):
        code = self.cleaned_data["code"].strip()
        if not code:
            raise ValidationError(_("Code is required."))
        return code

    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get("new_password")
        confirm_password = cleaned_data.get("confirm_password")

        if new_password and confirm_password and new_password != confirm_password:
            raise ValidationError(_("Passwords do not match."))

        return cleaned_data


class ChangePasswordForm(forms.Form):
    old_password = forms.CharField(widget=forms.PasswordInput)
    new_password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)

    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get("new_password")
        confirm_password = cleaned_data.get("confirm_password")

        if new_password and confirm_password and new_password != confirm_password:
            raise ValidationError(_("Passwords do not match."))

        return cleaned_data


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = (
            "username",
            "email",
            "phone_number",
            "bio",
            'image',
            "preferred_contact_method",
        )

    def clean_username(self):
        username = self.cleaned_data["username"].strip()
        qs = User.objects.filter(username=username)

        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)

        if qs.exists():
            raise ValidationError(_("Username already exists."))

        return username

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if email:
            email = email.strip().lower()
            qs = User.objects.filter(email=email)

            if self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)

            if qs.exists():
                raise ValidationError(_("Email already exists."))
        return email

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get("phone_number")
        if phone_number:
            phone_number = "".join(phone_number.strip().split())
            qs = User.objects.filter(phone_number=phone_number)

            if self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)

            if qs.exists():
                raise ValidationError(_("Phone number already exists."))
        return phone_number

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get("email")
        phone_number = cleaned_data.get("phone_number")
        preferred_contact_method = cleaned_data.get("preferred_contact_method")

        if not email and not phone_number:
            raise ValidationError(_("You must provide either email or phone number."))

        if preferred_contact_method == VerificationChannel.EMAIL and not email:
            raise ValidationError(_("Preferred contact method is email, but email is empty."))

        if preferred_contact_method == VerificationChannel.PHONE and not phone_number:
            raise ValidationError(_("Preferred contact method is phone, but phone number is empty."))

        return cleaned_data
