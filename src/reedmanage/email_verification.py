"""Email verification utilities for user signup"""
from django.core.mail import send_mail
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.template.loader import render_to_string
from django.conf import settings
from django.contrib.auth.models import User


def send_verification_email(user, request):
    """Send email verification link to user"""
    token = default_token_generator.make_token(user)
    uid = urlsafe_base64_encode(force_bytes(user.pk))

    # Build verification URL
    domain = request.get_host()
    protocol = 'https' if request.is_secure() else 'http'
    verification_url = f"{protocol}://{domain}/verify-email/{uid}/{token}/"

    # Email subject and message
    subject = 'Verify your ReedManage account'
    message = f"""
Hello {user.first_name},

Thank you for signing up for ReedManage! Please verify your email address by clicking the link below:

{verification_url}

This link will expire in {settings.EMAIL_VERIFICATION_EXPIRY_HOURS} hours.

If you did not create an account, please ignore this email.

Best regards,
The ReedManage Team
"""

    # Send email
    try:
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Failed to send verification email: {e}")
        return False


def verify_email_token(uidb64, token):
    """Verify email token and activate user"""
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        return None

    # Check if token is valid
    if default_token_generator.check_token(user, token):
        # Activate user (we'll use is_active field)
        if not user.is_active:
            user.is_active = True
            user.save()
        return user

    return None
