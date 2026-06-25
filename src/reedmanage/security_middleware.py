import logging
import re
from django.http import HttpResponseForbidden

logger = logging.getLogger('django.security')

_SUSPICIOUS_PATTERNS = [
    re.compile(r'\bunion\b.{0,30}\bselect\b', re.IGNORECASE),
    re.compile(r'<script[\s>]', re.IGNORECASE),
    re.compile(r'(\.\./){3,}'),
]


class SuspiciousRequestMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        target = request.META.get('QUERY_STRING', '') + request.path
        for pattern in _SUSPICIOUS_PATTERNS:
            if pattern.search(target):
                logger.warning(
                    'Suspicious request blocked: %s from %s',
                    request.path,
                    request.META.get('REMOTE_ADDR', 'unknown'),
                )
                return HttpResponseForbidden('Forbidden')
        return self.get_response(request)


class SecurityHeadersMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        response.setdefault('X-Content-Type-Options', 'nosniff')
        response.setdefault('X-Frame-Options', 'DENY')
        response.setdefault('Referrer-Policy', 'strict-origin-when-cross-origin')
        return response
