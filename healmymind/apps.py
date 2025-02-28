from django.apps import AppConfig
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class healmymindConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'healmymind'

    def ready(self):
        """
        Initialize app configurations and connect signals.
        """
        try:
            # Import signals
            import healmymind.signals

            # Initialize OpenAI
            if hasattr(settings, 'OPENAI_API_KEY'):
                import openai
                openai.api_key = settings.OPENAI_API_KEY
            else:
                logger.warning("OpenAI API key not configured")

            # Set up logging
            logging.basicConfig(
                level=logging.INFO,
                format='%(asctime)s [%(levelname)s] %(message)s',
                handlers=[
                    logging.StreamHandler(),
                    logging.FileHandler('healmymind.log')
                ]
            )

            logger.info("healmymind application initialized successfully")

        except Exception as e:
            logger.error(f"Error initializing healmymind application: {str(e)}")

class UsersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'users'

    def ready(self):
        """
        Initialize users app configurations.
        """
        try:
            # Import signals
            import users.signals

            logger.info("Users application initialized successfully")

        except Exception as e:
            logger.error(f"Error initializing Users application: {str(e)}")

class TestsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'tests'

    def ready(self):
        """
        Initialize tests app configurations.
        """
        try:
            # Import signals
            import tests.signals

            # Load test data if needed
            from django.core.management import call_command
            if settings.DEBUG:
                try:
                    call_command('loaddata', 'initial_tests')
                except Exception as e:
                    logger.warning(f"Could not load initial test data: {str(e)}")

            logger.info("Tests application initialized successfully")

        except Exception as e:
            logger.error(f"Error initializing Tests application: {str(e)}")

class BlogConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'blog'

    def ready(self):
        """
        Initialize blog app configurations.
        """
        try:
            # Import signals
            import blog.signals

            logger.info("Blog application initialized successfully")

        except Exception as e:
            logger.error(f"Error initializing Blog application: {str(e)}")

class ChatConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'chat'

    def ready(self):
        """
        Initialize chat app configurations.
        """
        try:
            # Import signals
            import chat.signals

            # Initialize chat bot if needed
            if hasattr(settings, 'OPENAI_API_KEY'):
                from chat.bot import initialize_bot
                initialize_bot()
            else:
                logger.warning("Chat bot initialization skipped: OpenAI API key not configured")

            logger.info("Chat application initialized successfully")

        except Exception as e:
            logger.error(f"Error initializing Chat application: {str(e)}")

def setup_periodic_tasks():
    """
    Set up periodic tasks for the application.
    """
    try:
        from django_celery_beat.models import PeriodicTask, IntervalSchedule
        
        # Create schedules
        hourly, _ = IntervalSchedule.objects.get_or_create(
            every=1,
            period=IntervalSchedule.HOURS,
        )
        
        daily, _ = IntervalSchedule.objects.get_or_create(
            every=1,
            period=IntervalSchedule.DAYS,
        )
        
        # Schedule tasks
        PeriodicTask.objects.get_or_create(
            name='cleanup_expired_tokens',
            task='users.tasks.cleanup_expired_tokens',
            interval=daily,
        )
        
        PeriodicTask.objects.get_or_create(
            name='update_analytics',
            task='healmymind.tasks.update_analytics',
            interval=hourly,
        )
        
        logger.info("Periodic tasks configured successfully")
        
    except Exception as e:
        logger.error(f"Error setting up periodic tasks: {str(e)}")
