from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.conf import settings
from django_ratelimit.decorators import ratelimit
from .forms import LoginForm, SignUpForm
from .email_verification import send_verification_email, verify_email_token
from usersettings.models import Checkbox_for_setting


def home_view(request):
    return render(request, 'home.html', {})


@ratelimit(key='ip', rate='50/h', method='POST', block=True)  # Increased for testing
def signup(request):
    """User signup with email verification"""
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            # Save user but set as inactive if email verification is required
            user = form.save(commit=False)

            if settings.EMAIL_VERIFICATION_REQUIRED:
                user.is_active = False  # User must verify email before logging in
                user.save()

                # Send verification email
                if send_verification_email(user, request):
                    messages.success(
                        request,
                        'Account created! Please check your email to verify your account.'
                    )
                else:
                    messages.warning(
                        request,
                        'Account created but we could not send the verification email. Please contact support.'
                    )
                return redirect('login')
            else:
                # No email verification required - activate immediately
                user.is_active = True
                user.save()

                # Create default settings
                Checkbox_for_setting.objects.create(
                    user=user,
                    checkboxsetting='temperature,humidity,cane_brand,harvest_year,gouging_machine,cane_diamater,thicness,hardness,flexibility,density,shaper,'
                )

                # Log user in
                login(request, user)
                messages.success(request, 'Account created successfully!')
                return redirect('/')
    else:
        form = SignUpForm()

    return render(request, 'signup.html', {'form': form})


@ratelimit(key='ip', rate='50/h', method='POST', block=True)  # Increased for testing
def login_view(request):
    """User login with rate limiting"""
    error_message = None
    form = LoginForm()

    if request.method == 'POST':
        form = LoginForm(data=request.POST)
        if form.is_valid():
            username = request.POST.get('username')
            password = request.POST.get('password')
            # django-axes requires request parameter for authentication tracking
            user = authenticate(request=request, username=username, password=password)

            if user is not None:
                if not user.is_active:
                    error_message = 'Please verify your email address before logging in. Check your inbox for the verification link.'
                else:
                    login(request, user)
                    if request.GET.get('next'):
                        return redirect(request.GET.get('next'))
                    else:
                        return redirect('home')
            else:
                error_message = 'Invalid username or password. Please try again.'
        else:
            error_message = 'Please correct the errors below.'

    return render(request, 'login.html', {
        'form': form,
        'error_message': error_message
    })


def verify_email_view(request, uidb64, token):
    """Verify user email address"""
    user = verify_email_token(uidb64, token)

    if user is not None:
        # Create default settings if not exists
        Checkbox_for_setting.objects.get_or_create(
            user=user,
            defaults={
                'checkboxsetting': 'temperature,humidity,cane_brand,harvest_year,gouging_machine,cane_diamater,thicness,hardness,flexibility,density,shaper,'
            }
        )

        messages.success(request, 'Email verified successfully! You can now log in.')
        return redirect('login')
    else:
        messages.error(request, 'Invalid or expired verification link. Please contact support.')
        return redirect('home')


def privacy_policy_view(request):
    """Privacy policy page"""
    return render(request, 'legal/privacy.html', {})


def terms_of_service_view(request):
    """Terms of service page"""
    return render(request, 'legal/terms.html', {})


def custom_404(request, exception):
    """Custom 404 error page"""
    return render(request, '404.html', {}, status=404)


def custom_500(request):
    """Custom 500 error page"""
    return render(request, '500.html', {}, status=500)


# Test views for error pages (only use in development)
def test_404_view(request):
    """Test view to see custom 404 page"""
    return render(request, '404.html', {}, status=404)


def test_500_view(request):
    """Test view to see custom 500 page"""
    return render(request, '500.html', {}, status=500)
