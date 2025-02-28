from rest_framework.exceptions import APIException
from rest_framework import status
from typing import Optional, Any, Dict

class BaseAPIException(APIException):
    """
    Base exception for all custom API exceptions.
    """
    def __init__(self, detail: Optional[str] = None, code: Optional[str] = None):
        super().__init__(detail, code)
        self.error_type = self.__class__.__name__

    def get_full_details(self) -> Dict[str, Any]:
        """
        Get detailed error information.
        """
        return {
            'type': self.error_type,
            'detail': self.detail,
            'code': self.code,
            'status': self.status_code
        }

class ValidationError(BaseAPIException):
    """
    Exception for validation errors.
    """
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Invalid input.'
    default_code = 'validation_error'

class AuthenticationError(BaseAPIException):
    """
    Exception for authentication errors.
    """
    status_code = status.HTTP_401_UNAUTHORIZED
    default_detail = 'Authentication failed.'
    default_code = 'authentication_error'

class PermissionDenied(BaseAPIException):
    """
    Exception for permission errors.
    """
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = 'Permission denied.'
    default_code = 'permission_denied'

class ResourceNotFound(BaseAPIException):
    """
    Exception for not found resources.
    """
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = 'Resource not found.'
    default_code = 'not_found'

class ConflictError(BaseAPIException):
    """
    Exception for conflict errors.
    """
    status_code = status.HTTP_409_CONFLICT
    default_detail = 'Resource conflict.'
    default_code = 'conflict'

class RateLimitExceeded(BaseAPIException):
    """
    Exception for rate limit exceeded.
    """
    status_code = status.HTTP_429_TOO_MANY_REQUESTS
    default_detail = 'Rate limit exceeded.'
    default_code = 'rate_limit_exceeded'

class ServiceUnavailable(BaseAPIException):
    """
    Exception for service unavailability.
    """
    status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    default_detail = 'Service temporarily unavailable.'
    default_code = 'service_unavailable'

class DatabaseError(BaseAPIException):
    """
    Exception for database errors.
    """
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_detail = 'Database error occurred.'
    default_code = 'database_error'

class ExternalServiceError(BaseAPIException):
    """
    Exception for external service errors.
    """
    status_code = status.HTTP_502_BAD_GATEWAY
    default_detail = 'External service error.'
    default_code = 'external_service_error'

class InvalidTokenError(BaseAPIException):
    """
    Exception for invalid tokens.
    """
    status_code = status.HTTP_401_UNAUTHORIZED
    default_detail = 'Invalid or expired token.'
    default_code = 'invalid_token'

class UserNotVerifiedError(BaseAPIException):
    """
    Exception for unverified users.
    """
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = 'User not verified.'
    default_code = 'user_not_verified'

class TestNotAvailableError(BaseAPIException):
    """
    Exception for unavailable tests.
    """
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = 'Test not available.'
    default_code = 'test_not_available'

class InvalidTestSubmissionError(BaseAPIException):
    """
    Exception for invalid test submissions.
    """
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Invalid test submission.'
    default_code = 'invalid_test_submission'

class ChatbotError(BaseAPIException):
    """
    Exception for chatbot errors.
    """
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_detail = 'Chatbot error occurred.'
    default_code = 'chatbot_error'

class AIServiceError(BaseAPIException):
    """
    Exception for AI service errors.
    """
    status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    default_detail = 'AI service temporarily unavailable.'
    default_code = 'ai_service_error'

class MaintenanceModeError(BaseAPIException):
    """
    Exception for maintenance mode.
    """
    status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    default_detail = 'System is under maintenance.'
    default_code = 'maintenance_mode'
