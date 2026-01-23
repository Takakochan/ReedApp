# Security utilities for Reed Django App

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from functools import wraps
from .models import Reedsdata
import logging
from django.utils import timezone

# Set up security logging
security_logger = logging.getLogger('reedsdata.security')

def require_reed_owner(view_func):
    """Decorator to ensure users can only access their own reed data"""
    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        # Get reed ID from URL parameters
        reed_id = kwargs.get('reed_id') or kwargs.get('pk') or kwargs.get('id')

        if reed_id:
            try:
                reed = get_object_or_404(Reedsdata, pk=reed_id)

                # Check if user owns this reed or is staff
                if reed.reedauthor != request.user and not request.user.is_staff:
                    security_logger.warning(f'Unauthorized access attempt: User {request.user.id} tried to access reed {reed_id} owned by {reed.reedauthor.id}')
                    raise PermissionDenied("You can only access your own reed data")

            except Reedsdata.DoesNotExist:
                security_logger.warning(f'Access attempt to non-existent reed {reed_id} by user {request.user.id}')
                raise PermissionDenied("Reed not found")

        return view_func(request, *args, **kwargs)
    return wrapper

def log_suspicious_activity(activity_type):
    """Decorator to log suspicious activities"""
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            # Log the activity
            security_logger.info(f'{activity_type}: User {request.user.id} from IP {get_client_ip(request)}')
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator

def get_client_ip(request):
    """Get client IP address"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def rate_limit_user(max_requests=20, window_minutes=15):
    """Simple rate limiting per user"""
    user_requests = {}

    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return view_func(request, *args, **kwargs)

            user_id = request.user.id
            now = timezone.now()

            # Clean old requests
            if user_id in user_requests:
                user_requests[user_id] = [req_time for req_time in user_requests[user_id]
                                        if (now - req_time).seconds < window_minutes * 60]
            else:
                user_requests[user_id] = []

            # Check rate limit
            if len(user_requests[user_id]) >= max_requests:
                security_logger.warning(f'Rate limit exceeded by user {user_id} from IP {get_client_ip(request)}')
                from django.http import HttpResponseTooManyRequests
                return HttpResponseTooManyRequests("Too many requests. Please try again later.")

            # Add current request
            user_requests[user_id].append(now)
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator
