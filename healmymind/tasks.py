from celery import shared_task
from django.core.cache import cache
from django.utils import timezone
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.db.models import Count, Avg
from datetime import timedelta
import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

# Analytics Tasks
@shared_task
def update_analytics() -> None:
    """
    Update analytics data for the dashboard.
    """
    try:
        from tests.models import TestResult
        from blog.models import Post
        from chat.models import Conversation
        
        now = timezone.now()
        last_30_days = now - timedelta(days=30)
        
        # Test analytics
        test_stats = TestResult.objects.filter(
            completed_at__gte=last_30_days
        ).aggregate(
            total_tests=Count('id'),
            avg_score=Avg('score')
        )
        
        # Blog analytics
        blog_stats = Post.objects.filter(
            published_at__gte=last_30_days
        ).aggregate(
            total_posts=Count('id'),
            avg_views=Avg('views_count'),
            avg_likes=Avg('likes_count')
        )
        
        # Chat analytics
        chat_stats = Conversation.objects.filter(
            created_at__gte=last_30_days
        ).aggregate(
            total_conversations=Count('id'),
            avg_messages=Avg('messages__count')
        )
        
        # Cache the results
        analytics_data = {
            'test_stats': test_stats,
            'blog_stats': blog_stats,
            'chat_stats': chat_stats,
            'updated_at': now.isoformat()
        }
        
        cache.set('analytics_data', analytics_data, timeout=3600)  # 1 hour cache
        logger.info("Analytics data updated successfully")
        
    except Exception as e:
        logger.error(f"Error updating analytics: {str(e)}")

# Email Tasks
@shared_task
def send_bulk_email(subject: str, template_name: str, context: Dict[str, Any], recipient_list: List[str]) -> None:
    """
    Send bulk emails using a template.
    """
    try:
        html_message = render_to_string(template_name, context)
        
        for recipient in recipient_list:
            try:
                send_mail(
                    subject=subject,
                    message='',
                    html_message=html_message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[recipient],
                    fail_silently=False
                )
                logger.info(f"Email sent successfully to {recipient}")
                
            except Exception as e:
                logger.error(f"Error sending email to {recipient}: {str(e)}")
                
    except Exception as e:
        logger.error(f"Error in bulk email task: {str(e)}")

@shared_task
def send_test_results_email(user_email: str, test_result_id: int) -> None:
    """
    Send test results email to user.
    """
    try:
        from tests.models import TestResult
        
        result = TestResult.objects.get(id=test_result_id)
        context = {
            'test_name': result.test.name,
            'score': result.score,
            'severity': result.severity,
            'recommendations': result.recommendations
        }
        
        html_message = render_to_string('emails/test_results.html', context)
        
        send_mail(
            subject=f'Your {result.test.name} Results',
            message='',
            html_message=html_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user_email],
            fail_silently=False
        )
        
        logger.info(f"Test results email sent to {user_email}")
        
    except Exception as e:
        logger.error(f"Error sending test results email: {str(e)}")

# Cleanup Tasks
@shared_task
def cleanup_expired_tokens() -> None:
    """
    Clean up expired tokens from the database.
    """
    try:
        from rest_framework_simplejwt.token_blacklist.models import OutstandingToken, BlacklistedToken
        
        # Delete expired blacklisted tokens
        BlacklistedToken.objects.filter(
            token__expires_at__lt=timezone.now()
        ).delete()
        
        # Delete expired outstanding tokens
        OutstandingToken.objects.filter(
            expires_at__lt=timezone.now()
        ).delete()
        
        logger.info("Expired tokens cleaned up successfully")
        
    except Exception as e:
        logger.error(f"Error cleaning up expired tokens: {str(e)}")

@shared_task
def cleanup_old_chat_messages() -> None:
    """
    Clean up old chat messages to prevent database bloat.
    """
    try:
        from chat.models import Message
        
        # Keep messages for last 90 days
        cutoff_date = timezone.now() - timedelta(days=90)
        
        Message.objects.filter(
            created_at__lt=cutoff_date
        ).delete()
        
        logger.info("Old chat messages cleaned up successfully")
        
    except Exception as e:
        logger.error(f"Error cleaning up old chat messages: {str(e)}")

# AI Tasks
@shared_task
def generate_blog_suggestions() -> None:
    """
    Generate blog post suggestions using AI.
    """
    try:
        import openai
        from blog.models import Post
        
        # Get recent popular topics
        popular_topics = Post.objects.filter(
            published_at__gte=timezone.now() - timedelta(days=30)
        ).order_by('-views_count')[:5]
        
        topics = [post.title for post in popular_topics]
        
        # Generate suggestions using GPT
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": "You are a mental health content strategist."
                },
                {
                    "role": "user",
                    "content": f"Based on these popular topics: {topics}, suggest 5 new blog post ideas."
                }
            ]
        )
        
        suggestions = response.choices[0].message.content
        
        # Cache the suggestions
        cache.set('blog_suggestions', suggestions, timeout=86400)  # 24 hours
        
        logger.info("Blog suggestions generated successfully")
        
    except Exception as e:
        logger.error(f"Error generating blog suggestions: {str(e)}")

# Monitoring Tasks
@shared_task
def monitor_system_health() -> None:
    """
    Monitor system health and send alerts if needed.
    """
    try:
        from django.db import connections
        from django.db.utils import OperationalError
        
        # Check database connection
        db_healthy = True
        try:
            connections['default'].cursor()
        except OperationalError:
            db_healthy = False
        
        # Check cache connection
        cache_healthy = cache.get('health_check') is not None
        
        # Check disk usage
        import shutil
        disk = shutil.disk_usage('/')
        disk_usage = disk.used / disk.total
        disk_healthy = disk_usage < 0.9  # Alert if over 90% usage
        
        if not all([db_healthy, cache_healthy, disk_healthy]):
            # Send alert
            send_mail(
                subject='System Health Alert',
                message=f'System health check failed:\nDatabase: {db_healthy}\nCache: {cache_healthy}\nDisk: {disk_healthy}',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=settings.ADMIN_EMAILS,
                fail_silently=True
            )
            
        logger.info("System health check completed")
        
    except Exception as e:
        logger.error(f"Error in system health check: {str(e)}")
