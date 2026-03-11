import random
from datetime import timedelta

from django.contrib.auth import authenticate
from django.utils import timezone
from django.core.exceptions import ValidationError

from .models import User, VerificationCode, VerificationChannel, VerificationPurpose, VerificationStatus


def generate_code():
    """Generate 6 digit verification code."""
    return str(random.randint(100000, 999999))


def create_verification_code(*, user, channel, purpose, target):
    """Create verification code object."""
    code = generate_code()

    verification = VerificationCode.objects.create(
        user=user,
        channel=channel,
        purpose=purpose,
        target=target,
        code=code,
        expires_at=timezone.now() + timedelta(minutes=10),
    )

    # здесь будет отправка email или sms
    print(f"Verification code for {target}: {code}")

    return verification


# ===============================
# SIGNUP
# ===============================

def register_user(*, username, password, role, email=None, phone_number=None):
    """Register user and send verification code."""

    if not email and not phone_number:
        raise ValidationError("Email or phone number must be provided")

    user = User.objects.create_user(
        username=username,
        password=password,
        role=role,
        email=email,
        phone_number=phone_number,
    )

    if email:
        channel = VerificationChannel.EMAIL
        target = email
    else:
        channel = VerificationChannel.PHONE
        target = phone_number

    create_verification_code(
        user=user,
        channel=channel,
        purpose=VerificationPurpose.SIGNUP,
        target=target,
    )

    return user


# ===============================
# VERIFY SIGNUP
# ===============================

def verify_signup_code(*, user, code):
    """Verify signup code and activate user."""

    try:
        verification = VerificationCode.objects.get(
            user=user,
            code=code,
            purpose=VerificationPurpose.SIGNUP,
            status=VerificationStatus.NEW,
        )
    except VerificationCode.DoesNotExist:
        raise ValidationError("Invalid verification code")

    if verification.is_expired:
        verification.mark_expired()
        raise ValidationError("Verification code expired")

    verification.mark_used()

    user.is_active = True

    if verification.channel == VerificationChannel.EMAIL:
        user.is_email_verified = True

    if verification.channel == VerificationChannel.PHONE:
        user.is_phone_verified = True

    user.save(update_fields=["is_active", "is_email_verified", "is_phone_verified"])

    return user


# ===============================
# LOGIN
# ===============================

def authenticate_user(identifier, password):
    """
    Login by username, email or phone.
    """

    user = (
        User.objects.filter(username=identifier).first()
        or User.objects.filter(email=identifier).first()
        or User.objects.filter(phone_number=identifier).first()
    )

    if not user:
        raise ValidationError("User not found")

    user = authenticate(username=user.username, password=password)

    if not user:
        raise ValidationError("Invalid password")

    if not user.is_active:
        raise ValidationError("User account is not active")

    return user


# ===============================
# FORGOT PASSWORD
# ===============================

def request_password_reset(identifier):
    """
    Send reset password code.
    """

    user = (
        User.objects.filter(username=identifier).first()
        or User.objects.filter(email=identifier).first()
        or User.objects.filter(phone_number=identifier).first()
    )

    if not user:
        raise ValidationError("User not found")

    if user.email:
        channel = VerificationChannel.EMAIL
        target = user.email
    else:
        channel = VerificationChannel.PHONE
        target = user.phone_number

    create_verification_code(
        user=user,
        channel=channel,
        purpose=VerificationPurpose.RESET_PASSWORD,
        target=target,
    )

    return user


# ===============================
# RESET PASSWORD
# ===============================

def reset_password(*, user, code, new_password):
    """Reset password using verification code."""

    try:
        verification = VerificationCode.objects.get(
            user=user,
            code=code,
            purpose=VerificationPurpose.RESET_PASSWORD,
            status=VerificationStatus.NEW,
        )
    except VerificationCode.DoesNotExist:
        raise ValidationError("Invalid verification code")

    if verification.is_expired:
        verification.mark_expired()
        raise ValidationError("Verification code expired")

    verification.mark_used()

    user.set_password(new_password)
    user.save(update_fields=["password"])

    return user


# ===============================
# CHANGE PASSWORD
# ===============================

def change_password(*, user, old_password, new_password):
    """Change password for logged in user."""

    if not user.check_password(old_password):
        raise ValidationError("Old password is incorrect")

    user.set_password(new_password)
    user.save(update_fields=["password"])

    return user