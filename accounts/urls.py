from django.urls import path

from .views import (
    change_password_view,
    freelancer_profile_view,
    forgot_password_view,
    login_view,
    logout_view,
    profile_update_view,
    profile_view,
    reset_password_view,
    signup_view,
    verify_signup_code_view,
)

app_name = "accounts"

urlpatterns = [
    path("signup/", signup_view, name="signup"),
    path("verify-signup-code/", verify_signup_code_view, name="verify-signup-code"),
    path("login/", login_view, name="login"),
    path("logout/", logout_view, name="logout"),
    path("profile/", profile_view, name="profile"),
    path("freelancers/<int:pk>/", freelancer_profile_view, name="freelancer-profile"),
    path("profile/update/", profile_update_view, name="profile-update"),
    path("forgot-password/", forgot_password_view, name="forgot-password"),
    path("reset-password/", reset_password_view, name="reset-password"),
    path("change-password/", change_password_view, name="change-password"),
]
