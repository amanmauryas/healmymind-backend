import os
from celery import Celery
from django.conf import settings
from celery.schedules import crontab
import logging

logger = logging.getLogger(__name__)

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'healmymind.settings')

app = Celery('healmymind')

# Configure Celery using Django settings
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()

# Configure periodic tasks
app.conf.beat_schedule = {
    'update-analytics': {
        'task': 'healmymind.tasks.update_analytics',
        'schedule': crontab(minute='0', hour='*/1'),  # Every hour
    },
    'cleanup-expired-tokens': {
        'task': 'healmymind.tasks.cleanup_expired_tokens',
        'schedule': crontab(minute='0', hour='0'),  # Daily at midnight
    },
    'cleanup-old-chat-messages': {
        'task': 'healmymind.tasks.cleanup_old_chat_messages',
        'schedule': crontab(minute='0', hour='3'),  # Daily at 3 AM
    },
    'generate-blog-suggestions': {
        'task': 'healmymind.tasks.generate_blog_suggestions',
        'schedule': crontab(minute='0', hour='4'),  # Daily at 4 AM
    },
    'monitor-system-health': {
        'task': 'healmymind.tasks.monitor_system_health',
        'schedule': crontab(minute='*/15'),  # Every 15 minutes
    },
}

# Configure Celery
app.conf.update(
    # Broker settings
    broker_url=settings.CELERY_BROKER_URL,
    result_backend=settings.CELERY_RESULT_BACKEND,
    
    # Task settings
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    
    # Task execution settings
    task_time_limit=3600,  # 1 hour
    task_soft_time_limit=3540,  # 59 minutes
    worker_max_tasks_per_child=200,
    worker_prefetch_multiplier=4,
    
    # Result settings
    result_expires=3600,  # 1 hour
    
    # Error handling
    task_reject_on_worker_lost=True,
    task_acks_late=True,
    
    # Logging
    worker_log_format='[%(asctime)s: %(levelname)s/%(processName)s] %(message)s',
    worker_task_log_format='[%(asctime)s: %(levelname)s/%(processName)s] [%(task_name)s(%(task_id)s)] %(message)s',
)

@app.task(bind=True)
def debug_task(self):
    """Task to verify Celery is working."""
    logger.info(f'Request: {self.request!r}')

@app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    """Set up any additional periodic tasks."""
    try:
        # Add any dynamic periodic tasks here
        pass
    except Exception as e:
        logger.error(f"Error setting up periodic tasks: {str(e)}")

@app.on_after_finalize.connect
def setup_cloud_events(sender, **kwargs):
    """Set up cloud event handlers."""
    try:
        # Add any cloud event handlers here
        pass
    except Exception as e:
        logger.error(f"Error setting up cloud events: {str(e)}")

# Error handling
@app.task(bind=True)
def handle_task_error(self, task_id, exc, traceback):
    """Handle task errors."""
    logger.error(f"Task {task_id} failed: {exc}\n{traceback}")
    
    # Notify admins
    if hasattr(settings, 'ADMIN_EMAILS'):
        from django.core.mail import send_mail
        send_mail(
            subject=f'Task Error: {task_id}',
            message=f'Task failed with error:\n{exc}\n\nTraceback:\n{traceback}',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=settings.ADMIN_EMAILS,
            fail_silently=True
        )

app.conf.task_error_handler = 'healmymind.celery.handle_task_error'

# Custom task base class
class BaseTask(app.Task):
    """Base task class with error handling and logging."""
    
    abstract = True
    
    def on_failure(self, exc, task_id, args, kwargs, einfo):
        """Handle task failure."""
        logger.error(f'Task {task_id} failed: {exc}')
        super().on_failure(exc, task_id, args, kwargs, einfo)
    
    def on_retry(self, exc, task_id, args, kwargs, einfo):
        """Handle task retry."""
        logger.warning(f'Task {task_id} retrying: {exc}')
        super().on_retry(exc, task_id, args, kwargs, einfo)
    
    def on_success(self, retval, task_id, args, kwargs):
        """Handle task success."""
        logger.info(f'Task {task_id} completed successfully')
        super().on_success(retval, task_id, args, kwargs)

app.Task = BaseTask

if __name__ == '__main__':
    app.start()
