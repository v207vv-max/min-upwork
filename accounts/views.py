from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .forms import (
    ChangePasswordForm,
    ForgotPasswordForm,
    LoginForm,
    ProfileUpdateForm,
    ResetPasswordForm,
    SignUpForm,
    VerifyCodeForm,
)
from .models import User
from .services import (
    authenticate_user,
    change_password,
    register_user,
    request_password_reset,
    reset_password,
    verify_signup_code,
)


def signup_view(request):
    if request.user.is_authenticated:
        return redirect("accounts:profile")

    form = SignUpForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        user = register_user(
            username=form.cleaned_data["username"],
            password=form.cleaned_data["password"],
            role=form.cleaned_data["role"],
            email=form.cleaned_data.get("email"),
            phone_number=form.cleaned_data.get("phone_number"),
        )

        if form.cleaned_data.get("preferred_contact_method"):
            user.preferred_contact_method = form.cleaned_data["preferred_contact_method"]
            user.save(update_fields=["preferred_contact_method"])

        request.session["pending_user_id"] = user.id
        messages.success(request, "Verification code was sent successfully.")
        return redirect("accounts:verify-signup-code")

    return render(request, "accounts/signup.html", {"form": form})


def verify_signup_code_view(request):
    if request.user.is_authenticated:
        return redirect("accounts:profile")

    user_id = request.session.get("pending_user_id")
    if not user_id:
        messages.error(request, "No pending signup session found.")
        return redirect("accounts:signup")

    user = get_object_or_404(User, id=user_id)
    form = VerifyCodeForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        user = verify_signup_code(
            user=user,
            code=form.cleaned_data["code"],
        )
        request.session.pop("pending_user_id", None)
        login(request, user)
        messages.success(request, "Account verified successfully.")
        return redirect("accounts:profile")

    return render(
        request,
        "accounts/verify_signup_code.html",
        {"form": form, "pending_user": user},
    )


def login_view(request):
    if request.user.is_authenticated:
        return redirect("accounts:profile")

    form = LoginForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        user = authenticate_user(
            identifier=form.cleaned_data["identifier"],
            password=form.cleaned_data["password"],
        )
        login(request, user)
        messages.success(request, "You logged in successfully.")
        return redirect("accounts:profile")

    return render(request, "accounts/login.html", {"form": form})


@login_required
def logout_view(request):
    logout(request)
    messages.success(request, "You logged out successfully.")
    return redirect("accounts:login")


@login_required
def profile_view(request):
    return render(request, "accounts/profile.html", {"user_obj": request.user})


@login_required
def profile_update_view(request):
    form = ProfileUpdateForm(request.POST or None, instance=request.user)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Profile updated successfully.")
        return redirect("accounts:profile")

    return render(request, "accounts/profile_update.html", {"form": form})


def forgot_password_view(request):
    if request.user.is_authenticated:
        return redirect("accounts:profile")

    form = ForgotPasswordForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        user = request_password_reset(
            identifier=form.cleaned_data["identifier"],
        )

        request.session["reset_user_id"] = user.id
        messages.success(request, "Password reset code was sent.")
        return redirect("accounts:reset-password")

    return render(request, "accounts/forgot_password.html", {"form": form})


def reset_password_view(request):
    if request.user.is_authenticated:
        return redirect("accounts:profile")

    user_id = request.session.get("reset_user_id")
    if not user_id:
        messages.error(request, "No password reset request found.")
        return redirect("accounts:forgot-password")

    user = get_object_or_404(User, id=user_id)
    form = ResetPasswordForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        reset_password(
            user=user,
            code=form.cleaned_data["code"],
            new_password=form.cleaned_data["new_password"],
        )
        request.session.pop("reset_user_id", None)
        messages.success(request, "Password was reset successfully.")
        return redirect("accounts:login")

    return render(
        request,
        "accounts/reset_password.html",
        {"form": form, "reset_user": user},
    )


@login_required
def change_password_view(request):
    form = ChangePasswordForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        change_password(
            user=request.user,
            old_password=form.cleaned_data["old_password"],
            new_password=form.cleaned_data["new_password"],
        )
        messages.success(request, "Password changed successfully. Please log in again.")
        logout(request)
        return redirect("accounts:login")

    return render(request, "accounts/change_password.html", {"form": form})