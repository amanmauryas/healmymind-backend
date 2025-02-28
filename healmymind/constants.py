from typing import Dict, List, Tuple

# Authentication Constants
TOKEN_EXPIRY_DAYS = 7
REFRESH_TOKEN_EXPIRY_DAYS = 30
PASSWORD_RESET_EXPIRY_HOURS = 24
EMAIL_VERIFICATION_EXPIRY_HOURS = 48
MAX_LOGIN_ATTEMPTS = 5
LOGIN_COOLDOWN_MINUTES = 15

# Rate Limiting
RATE_LIMIT_WINDOW = 3600  # 1 hour in seconds
RATE_LIMIT_MAX_REQUESTS = 1000

# Pagination
DEFAULT_PAGE_SIZE = 10
MAX_PAGE_SIZE = 100
INFINITE_SCROLL_SIZE = 20

# File Upload
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
ALLOWED_FILE_TYPES = ['image/jpeg', 'image/png', 'image/gif']
MAX_IMAGE_DIMENSIONS = (1920, 1080)

# Cache
CACHE_TTL = 3600  # 1 hour in seconds
CACHE_PREFIX = 'healmymind:'

# Mental Health Tests
TEST_TYPES: List[Tuple[str, str]] = [
    ('PHQ9', 'Depression Screening (PHQ-9)'),
    ('GAD7', 'Anxiety Screening (GAD-7)'),
    ('PCL5', 'PTSD Screening (PCL-5)'),
]

SEVERITY_LEVELS: List[Tuple[str, str]] = [
    ('MINIMAL', 'Minimal'),
    ('MILD', 'Mild'),
    ('MODERATE', 'Moderate'),
    ('SEVERE', 'Severe'),
]

# Scoring Ranges
PHQ9_RANGES: List[Dict] = [
    {'min': 0, 'max': 4, 'severity': 'MINIMAL', 'description': 'Minimal depression'},
    {'min': 5, 'max': 9, 'severity': 'MILD', 'description': 'Mild depression'},
    {'min': 10, 'max': 14, 'severity': 'MODERATE', 'description': 'Moderate depression'},
    {'min': 15, 'max': 27, 'severity': 'SEVERE', 'description': 'Severe depression'},
]

GAD7_RANGES: List[Dict] = [
    {'min': 0, 'max': 4, 'severity': 'MINIMAL', 'description': 'Minimal anxiety'},
    {'min': 5, 'max': 9, 'severity': 'MILD', 'description': 'Mild anxiety'},
    {'min': 10, 'max': 14, 'severity': 'MODERATE', 'description': 'Moderate anxiety'},
    {'min': 15, 'max': 21, 'severity': 'SEVERE', 'description': 'Severe anxiety'},
]

# Blog Constants
POST_STATUS_CHOICES: List[Tuple[str, str]] = [
    ('DRAFT', 'Draft'),
    ('PUBLISHED', 'Published'),
]

BLOG_CATEGORIES: List[str] = [
    'Mental Health',
    'Anxiety',
    'Depression',
    'PTSD',
    'Self-Care',
    'Wellness',
    'Research',
    'Treatment',
]

# Chat Constants
MESSAGE_TYPES: List[Tuple[str, str]] = [
    ('USER', 'User Message'),
    ('BOT', 'Bot Message'),
    ('SYSTEM', 'System Message'),
]

FEEDBACK_TYPES: List[Tuple[str, str]] = [
    ('HELPFUL', 'Helpful'),
    ('NOT_HELPFUL', 'Not Helpful'),
    ('INAPPROPRIATE', 'Inappropriate'),
    ('OTHER', 'Other'),
]

RESOURCE_TYPES: List[Tuple[str, str]] = [
    ('CRISIS', 'Crisis Support'),
    ('THERAPY', 'Therapy Resources'),
    ('SELF_HELP', 'Self Help'),
    ('COMMUNITY', 'Community Support'),
]

# Emergency Resources
EMERGENCY_CONTACTS: Dict[str, str] = {
    'suicide_prevention': '988',
    'crisis_text': '741741',
    'emergency': '911',
}

# API Versions
API_VERSIONS: List[str] = ['1.0', '1.1']
CURRENT_API_VERSION = '1.0'
DEPRECATED_VERSIONS: List[str] = []

# Error Messages
ERROR_MESSAGES = {
    'authentication': 'Authentication credentials were not provided or are invalid.',
    'permission': 'You do not have permission to perform this action.',
    'not_found': 'The requested resource was not found.',
    'validation': 'The provided data is invalid.',
    'rate_limit': 'Too many requests. Please try again later.',
    'server_error': 'An unexpected error occurred. Please try again later.',
}

# Success Messages
SUCCESS_MESSAGES = {
    'created': 'Resource created successfully.',
    'updated': 'Resource updated successfully.',
    'deleted': 'Resource deleted successfully.',
    'password_reset': 'Password reset email has been sent.',
    'email_verified': 'Email verified successfully.',
}

# Maintenance Mode
MAINTENANCE_MODE = False
MAINTENANCE_MODE_EXCLUDED_PATHS = [
    '/api/health/',
    '/api/status/',
]

# Analytics
ANALYTICS_RETENTION_DAYS = 30
METRICS_COLLECTION_ENABLED = True

# AI Configuration
AI_MODEL_CONFIG = {
    'chat': {
        'model': 'gpt-4',
        'temperature': 0.7,
        'max_tokens': 150,
    },
    'analysis': {
        'model': 'gpt-4',
        'temperature': 0.3,
        'max_tokens': 500,
    },
}

# Feature Flags
FEATURES = {
    'ai_chat': True,
    'blog': True,
    'test_suggestions': True,
    'email_verification': True,
    'social_auth': False,
}
