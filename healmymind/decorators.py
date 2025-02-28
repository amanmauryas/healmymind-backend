import time
import functools
from typing import Callable, Any, Dict
from django.core.cache import cache
from django.conf import settings
from rest_framework.response import Response
from .exceptions import RateLimitExceeded, ServiceUnavailable
from .utils import format_error_response
import logging

logger = logging.getLogger(__name__)

def rate_limit(key: str = '', rate: int = 100, period: int = 3600) -> Callable:
    """
    Rate limiting decorator for API views.
    
    Args:
        key: String to identify the rate limit bucket
        rate: Number of allowed requests per period
        period: Time period in seconds
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(self, request, *args, **kwargs):
            if settings.DEBUG:
                return func(self, request, *args, **kwargs)

            # Generate cache key
            user_id = request.user.id if request.user.is_authenticated else 'anonymous'
            cache_key = f'rate_limit:{key}:{user_id}'

            # Get current count
            count = cache.get(cache_key, 0)
            
            if count >= rate:
                raise RateLimitExceeded()

            # Increment count
            cache.set(cache_key, count + 1, period)
            
            return func(self, request, *args, **kwargs)
        return wrapper
    return decorator

def log_execution_time(func: Callable) -> Callable:
    """
    Decorator to log function execution time.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        
        logger.info(
            f"Function {func.__name__} took {(end_time - start_time):.2f} seconds to execute"
        )
        return result
    return wrapper

def cache_response(timeout: int = 300) -> Callable:
    """
    Cache decorator for API responses.
    
    Args:
        timeout: Cache timeout in seconds
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(self, request, *args, **kwargs):
            # Generate cache key
            cache_key = f"view_cache:{request.path}:{request.user.id if request.user.is_authenticated else 'anonymous'}"
            
            # Try to get from cache
            cached_response = cache.get(cache_key)
            if cached_response is not None:
                return Response(cached_response)
            
            # Get fresh response
            response = func(self, request, *args, **kwargs)
            
            # Cache the response data
            cache.set(cache_key, response.data, timeout)
            
            return response
        return wrapper
    return decorator

def require_feature_flag(flag_name: str) -> Callable:
    """
    Decorator to check if a feature flag is enabled.
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if not settings.FEATURES.get(flag_name, False):
                return Response(
                    format_error_response(
                        'feature_disabled',
                        f'The feature {flag_name} is currently disabled'
                    ),
                    status=404
                )
            return func(*args, **kwargs)
        return wrapper
    return decorator

def maintenance_mode_check(func: Callable) -> Callable:
    """
    Decorator to check if maintenance mode is enabled.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if getattr(settings, 'MAINTENANCE_MODE', False):
            raise ServiceUnavailable('System is under maintenance')
        return func(*args, **kwargs)
    return wrapper

def validate_request_data(*required_fields: str) -> Callable:
    """
    Decorator to validate required fields in request data.
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(self, request, *args, **kwargs):
            missing_fields = [
                field for field in required_fields
                if field not in request.data
            ]
            if missing_fields:
                return Response(
                    format_error_response(
                        'missing_fields',
                        f'Missing required fields: {", ".join(missing_fields)}'
                    ),
                    status=400
                )
            return func(self, request, *args, **kwargs)
        return wrapper
    return decorator

def track_analytics(event_type: str) -> Callable:
    """
    Decorator to track analytics events.
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(self, request, *args, **kwargs):
            response = func(self, request, *args, **kwargs)
            
            # Track the event
            analytics_data = {
                'event_type': event_type,
                'user_id': request.user.id if request.user.is_authenticated else None,
                'path': request.path,
                'method': request.method,
                'status_code': response.status_code,
                'timestamp': time.time()
            }
            
            # Log analytics data (implement your analytics solution)
            logger.info(f"Analytics Event: {analytics_data}")
            
            return response
        return wrapper
    return decorator

def handle_exceptions(func: Callable) -> Callable:
    """
    Decorator to handle exceptions and return formatted responses.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.exception("Error in API endpoint")
            return Response(
                format_error_response(
                    type(e).__name__,
                    str(e)
                ),
                status=getattr(e, 'status_code', 500)
            )
    return wrapper
