"""
WSGI config for healmymind project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/wsgi/
"""

import os
import sys
from pathlib import Path
from django.core.wsgi import get_wsgi_application
from whitenoise import WhiteNoise

# Add the project directory to the Python path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

# Set the Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'healmymind.settings')

try:
    # Initialize Django WSGI application
    application = get_wsgi_application()
    
    # Wrap the application with WhiteNoise for static file serving
    application = WhiteNoise(
        application,
        root=os.path.join(BASE_DIR, 'staticfiles'),
        prefix='static/'
    )
    
    # Configure WhiteNoise
    application.add_files(
        root=os.path.join(BASE_DIR, 'staticfiles'),
        prefix='static/'
    )
    
except Exception as e:
    import logging
    logging.error(f"Error initializing WSGI application: {str(e)}")
    raise

# Health check endpoint
def health_check(environ, start_response):
    """
    Simple health check endpoint for monitoring.
    """
    status = '200 OK'
    response_headers = [('Content-type', 'application/json')]
    start_response(status, response_headers)
    return [b'{"status": "healthy"}']

# Custom middleware for health checks
class HealthCheckMiddleware:
    def __init__(self, app):
        self.app = app
        self.health_url = '/health/'

    def __call__(self, environ, start_response):
        if environ.get('PATH_INFO') == self.health_url:
            return health_check(environ, start_response)
        return self.app(environ, start_response)

# Wrap the application with health check middleware
application = HealthCheckMiddleware(application)

# Error handling middleware
class ErrorHandlingMiddleware:
    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        try:
            return self.app(environ, start_response)
        except Exception as e:
            # Log the error
            import logging
            logging.exception("Error in WSGI application")
            
            # Return error response
            status = '500 Internal Server Error'
            response_headers = [('Content-type', 'application/json')]
            start_response(status, response_headers)
            return [b'{"error": "Internal Server Error"}']

# Wrap the application with error handling middleware
application = ErrorHandlingMiddleware(application)

# Security headers middleware
class SecurityHeadersMiddleware:
    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        def custom_start_response(status, headers, exc_info=None):
            # Add security headers
            security_headers = [
                ('X-Content-Type-Options', 'nosniff'),
                ('X-Frame-Options', 'DENY'),
                ('X-XSS-Protection', '1; mode=block'),
                ('Strict-Transport-Security', 'max-age=31536000; includeSubDomains'),
                ('Content-Security-Policy', "default-src 'self'"),
                ('Referrer-Policy', 'strict-origin-when-cross-origin'),
                ('Permissions-Policy', 'geolocation=(), microphone=(), camera=()'),
            ]
            headers.extend(security_headers)
            return start_response(status, headers, exc_info)
        
        return self.app(environ, custom_start_response)

# Wrap the application with security headers middleware
application = SecurityHeadersMiddleware(application)

# Request logging middleware
class RequestLoggingMiddleware:
    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        # Log request details
        import logging
        import time
        
        start_time = time.time()
        
        def custom_start_response(status, headers, exc_info=None):
            # Calculate request duration
            duration = time.time() - start_time
            
            # Log request details
            logging.info(
                f"Request: {environ.get('REQUEST_METHOD')} {environ.get('PATH_INFO')} "
                f"- Status: {status} - Duration: {duration:.3f}s"
            )
            
            return start_response(status, headers, exc_info)
        
        return self.app(environ, custom_start_response)

# Wrap the application with request logging middleware
application = RequestLoggingMiddleware(application)
