import time
import json
import logging
from django.http import JsonResponse
from django.conf import settings
from django.core.cache import cache
from django.utils.deprecation import MiddlewareMixin
from typing import Any, Callable

logger = logging.getLogger(__name__)

class RequestLoggingMiddleware(MiddlewareMixin):
    """
    Middleware to log all requests and their processing time.
    """
    def process_request(self, request):
        request.start_time = time.time()

    def process_response(self, request, response):
        if hasattr(request, 'start_time'):
            processing_time = time.time() - request.start_time
            log_data = {
                'path': request.path,
                'method': request.method,
                'processing_time': round(processing_time, 3),
                'status_code': response.status_code,
                'user': request.user.email if request.user.is_authenticated else 'anonymous'
            }
            logger.info(f"Request processed: {json.dumps(log_data)}")
        return response

class RateLimitMiddleware(MiddlewareMixin):
    """
    Middleware to implement rate limiting.
    """
    def process_request(self, request):
        if not settings.DEBUG:
            ip = self.get_client_ip(request)
            if self.is_rate_limited(ip):
                return JsonResponse({
                    'error': 'Rate limit exceeded. Please try again later.'
                }, status=429)

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0]
        return request.META.get('REMOTE_ADDR')

    def is_rate_limited(self, ip: str) -> bool:
        key = f'rate_limit:{ip}'
        requests = cache.get(key, 0)
        
        if requests >= settings.RATE_LIMIT_MAX_REQUESTS:
            return True
        
        cache.set(key, requests + 1, settings.RATE_LIMIT_WINDOW)
        return False

class APIVersionMiddleware(MiddlewareMixin):
    """
    Middleware to handle API versioning.
    """
    def process_request(self, request):
        version = request.headers.get('X-API-Version', '1.0')
        request.version = version

class ErrorHandlingMiddleware(MiddlewareMixin):
    """
    Middleware to handle exceptions and return appropriate JSON responses.
    """
    def process_exception(self, request, exception):
        if settings.DEBUG:
            return None

        error_data = {
            'error': str(exception),
            'type': exception.__class__.__name__
        }

        if hasattr(exception, 'status_code'):
            status_code = exception.status_code
        else:
            status_code = 500
            error_data['error'] = 'Internal Server Error'
            logger.exception('Unhandled exception occurred')

        return JsonResponse(error_data, status=status_code)

class MetricsMiddleware(MiddlewareMixin):
    """
    Middleware to collect metrics about API usage.
    """
    def process_request(self, request):
        request.start_time = time.time()

    def process_response(self, request, response):
        if hasattr(request, 'start_time'):
            duration = time.time() - request.start_time
            self.record_metrics(request, response, duration)
        return response

    def record_metrics(self, request: Any, response: Any, duration: float) -> None:
        metrics = {
            'path': request.path,
            'method': request.method,
            'status': response.status_code,
            'duration': duration,
            'timestamp': time.time()
        }
        
        # Store metrics (implement your storage solution)
        logger.info(f"API Metrics: {json.dumps(metrics)}")

class JWTAuthMiddleware(MiddlewareMixin):
    """
    Middleware to handle JWT authentication.
    """
    def process_request(self, request):
        auth_header = request.headers.get('Authorization', '')
        if auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
            request.token = token
        else:
            request.token = None

class CORSMiddleware(MiddlewareMixin):
    """
    Middleware to handle CORS headers.
    """
    def process_response(self, request, response):
        response['Access-Control-Allow-Origin'] = settings.CORS_ORIGIN_WHITELIST
        response['Access-Control-Allow-Methods'] = 'GET, POST, PUT, PATCH, DELETE, OPTIONS'
        response['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-API-Version'
        response['Access-Control-Allow-Credentials'] = 'true'
        return response

class MaintenanceModeMiddleware(MiddlewareMixin):
    """
    Middleware to handle maintenance mode.
    """
    def process_request(self, request):
        if getattr(settings, 'MAINTENANCE_MODE', False):
            if not any(path in request.path for path in settings.MAINTENANCE_MODE_EXCLUDED_PATHS):
                return JsonResponse({
                    'error': 'System is under maintenance. Please try again later.'
                }, status=503)
