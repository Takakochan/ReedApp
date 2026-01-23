# Health check views for production monitoring

from django.http import JsonResponse, HttpResponse
from django.db import connection
from django.conf import settings
import time
import logging

logger = logging.getLogger(__name__)

def health_check(request):
    """Simple health check endpoint"""
    try:
        # Check database connection
        cursor = connection.cursor()
        cursor.execute("SELECT 1")
        cursor.fetchone()
        cursor.close()

        return JsonResponse({
            'status': 'healthy',
            'timestamp': time.time(),
            'debug': settings.DEBUG,
            'database': 'connected'
        })
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JsonResponse({
            'status': 'unhealthy',
            'timestamp': time.time(),
            'error': str(e)
        }, status=503)

def simple_health_check(request):
    """Simple text response for load balancers"""
    return HttpResponse('OK', content_type='text/plain')

def detailed_health_check(request):
    """Detailed health check for monitoring systems"""
    checks = {}
    overall_status = 'healthy'

    # Database check
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT 1")
        cursor.fetchone()
        cursor.close()
        checks['database'] = 'healthy'
    except Exception as e:
        checks['database'] = f'error: {str(e)}'
        overall_status = 'unhealthy'

    # File system check (logs directory)
    try:
        import os
        log_dir = os.path.join(settings.BASE_DIR, 'logs')
        if os.path.exists(log_dir) and os.access(log_dir, os.W_OK):
            checks['filesystem'] = 'healthy'
        else:
            checks['filesystem'] = 'warning: logs directory not writable'
    except Exception as e:
        checks['filesystem'] = f'error: {str(e)}'
        overall_status = 'unhealthy'

    # Memory usage check (basic)
    try:
        import psutil
        memory = psutil.virtual_memory()
        if memory.percent < 90:
            checks['memory'] = f'healthy ({memory.percent:.1f}% used)'
        else:
            checks['memory'] = f'warning ({memory.percent:.1f}% used)'
            if overall_status == 'healthy':
                overall_status = 'warning'
    except ImportError:
        checks['memory'] = 'psutil not installed'
    except Exception as e:
        checks['memory'] = f'error: {str(e)}'

    status_code = 200
    if overall_status == 'unhealthy':
        status_code = 503
    elif overall_status == 'warning':
        status_code = 200  # Still return 200 for warnings

    return JsonResponse({
        'status': overall_status,
        'timestamp': time.time(),
        'checks': checks,
        'version': '1.0.0'  # Update this with your app version
    }, status=status_code)
