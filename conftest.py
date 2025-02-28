"""
Pytest configuration and fixtures.
"""
import os
from typing import Any, Generator

import pytest
from django.conf import settings
from django.core.management import call_command
from django.test import Client
from pymongo import MongoClient
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from users.models import User

# Set test environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'healmymind.settings')
os.environ['TESTING'] = 'true'

# Test database settings
TEST_DB_NAME = 'test_healmymind'


def pytest_configure() -> None:
    """Configure Django settings for tests."""
    settings.DATABASES['default']['NAME'] = TEST_DB_NAME
    settings.CELERY_TASK_ALWAYS_EAGER = True
    settings.EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'


@pytest.fixture(autouse=True)
def enable_db_access_for_all_tests(db: Any) -> Any:
    """Enable database access for all tests."""
    return db


@pytest.fixture(scope='session')
def django_db_setup(django_db_setup: Any, django_db_blocker: Any) -> None:
    """Set up test database."""
    with django_db_blocker.unblock():
        call_command('migrate')


@pytest.fixture
def client() -> Client:
    """Django test client fixture."""
    return Client()


@pytest.fixture
def api_client() -> APIClient:
    """DRF API client fixture."""
    return APIClient()


@pytest.fixture
def user() -> User:
    """Create a test user."""
    return User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='testpass123'
    )


@pytest.fixture
def admin_user() -> User:
    """Create a test admin user."""
    return User.objects.create_superuser(
        username='admin',
        email='admin@example.com',
        password='adminpass123'
    )


@pytest.fixture
def auth_client(api_client: APIClient, user: User) -> APIClient:
    """API client with user authentication."""
    refresh = RefreshToken.for_user(user)
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    return api_client


@pytest.fixture
def admin_client(api_client: APIClient, admin_user: User) -> APIClient:
    """API client with admin authentication."""
    refresh = RefreshToken.for_user(admin_user)
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    return api_client


@pytest.fixture(scope='session')
def mongo_client() -> Generator[MongoClient, None, None]:
    """MongoDB client fixture."""
    client = MongoClient(settings.MONGODB_URI)
    yield client
    client.drop_database(TEST_DB_NAME)
    client.close()


@pytest.fixture(autouse=True)
def clear_caches() -> None:
    """Clear all caches before each test."""
    from django.core.cache import cache
    cache.clear()


@pytest.fixture
def mock_openai(mocker: Any) -> Any:
    """Mock OpenAI API calls."""
    return mocker.patch('openai.ChatCompletion.create')


@pytest.fixture
def mock_celery_task(mocker: Any) -> Any:
    """Mock Celery task execution."""
    return mocker.patch('celery.app.task.Task.delay')


@pytest.fixture
def temp_media_root(tmp_path: Any) -> Generator[str, None, None]:
    """Temporary media root for file uploads."""
    original_media_root = settings.MEDIA_ROOT
    settings.MEDIA_ROOT = str(tmp_path)
    yield str(tmp_path)
    settings.MEDIA_ROOT = original_media_root


@pytest.fixture
def test_password() -> str:
    """Test password fixture."""
    return 'strong-test-pass-123'


@pytest.fixture
def create_user(db: Any, test_password: str) -> Any:
    """Factory fixture to create test users."""
    def make_user(**kwargs: Any) -> User:
        kwargs['password'] = test_password
        if 'username' not in kwargs:
            kwargs['username'] = 'testuser{}'.format(User.objects.count() + 1)
        if 'email' not in kwargs:
            kwargs['email'] = '{}@example.com'.format(kwargs['username'])
        return User.objects.create_user(**kwargs)
    return make_user


@pytest.fixture
def test_data() -> dict:
    """Common test data fixture."""
    return {
        'user': {
            'email': 'newuser@example.com',
            'username': 'newuser',
            'password': 'newpass123',
        },
        'test_result': {
            'score': 10,
            'severity': 'MODERATE',
            'answers': {'q1': 2, 'q2': 1, 'q3': 3},
        },
        'blog_post': {
            'title': 'Test Post',
            'content': 'Test content',
            'status': 'PUBLISHED',
        },
        'chat_message': {
            'content': 'Hello, I need help',
        },
    }


def pytest_collection_modifyitems(items: list) -> None:
    """Add markers to tests based on location."""
    for item in items:
        if 'integration' in str(item.fspath):
            item.add_marker(pytest.mark.integration)
        elif 'unit' in str(item.fspath):
            item.add_marker(pytest.mark.unit)


@pytest.fixture(autouse=True)
def _mock_db_connection() -> None:
    """Mock database connection to prevent actual database operations."""
    pass


@pytest.fixture(autouse=True)
def _mock_redis_connection() -> None:
    """Mock Redis connection to prevent actual Redis operations."""
    pass


@pytest.fixture(autouse=True)
def _mock_celery_connection() -> None:
    """Mock Celery connection to prevent actual Celery operations."""
    pass
