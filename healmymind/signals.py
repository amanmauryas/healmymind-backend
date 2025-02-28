from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from django.core.cache import cache
from django.contrib.auth import get_user_model
from django.utils import timezone
from users.models import UserProfile
from tests.models import TestResult
from blog.models import Post, Comment
from chat.models import Message, ChatMetric
import logging

logger = logging.getLogger(__name__)
User = get_user_model()

# User Signals
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Create UserProfile when a new User is created."""
    if created:
        UserProfile.objects.create(user=instance)
        logger.info(f"Created profile for user {instance.email}")

@receiver(post_save, sender=User)
def invalidate_user_cache(sender, instance, **kwargs):
    """Invalidate user-related cache when User is updated."""
    cache.delete(f'user_profile_{instance.id}')
    cache.delete(f'user_tests_{instance.id}')

# Test Result Signals
@receiver(post_save, sender=TestResult)
def process_test_result(sender, instance, created, **kwargs):
    """Process new test results."""
    if created:
        # Update user's test history
        profile = instance.user.profile
        history = profile.test_history
        history.append({
            'test_id': str(instance.test.id),
            'test_name': instance.test.name,
            'score': instance.score,
            'severity': instance.severity,
            'date': timezone.now().isoformat()
        })
        profile.save()
        
        # Invalidate relevant caches
        cache.delete(f'user_tests_{instance.user.id}')
        cache.delete(f'test_stats_{instance.test.id}')
        
        logger.info(f"Processed test result for user {instance.user.email}")

# Blog Signals
@receiver(pre_save, sender=Post)
def prepare_post(sender, instance, **kwargs):
    """Prepare blog post before saving."""
    if not instance.pk:  # New post
        if not instance.excerpt and instance.content:
            # Generate excerpt from content
            instance.excerpt = instance.content[:200] + '...'

@receiver(post_save, sender=Post)
def handle_post_save(sender, instance, created, **kwargs):
    """Handle post-save actions for blog posts."""
    # Invalidate caches
    cache.delete(f'post_{instance.slug}')
    cache.delete('blog_posts_list')
    
    if created:
        logger.info(f"New blog post created: {instance.title}")

@receiver(post_save, sender=Comment)
def handle_comment_save(sender, instance, created, **kwargs):
    """Handle post-save actions for comments."""
    if created:
        # Update post's comment count
        post = instance.post
        post.comment_count = post.comments.count()
        post.save()
        
        # Invalidate caches
        cache.delete(f'post_comments_{post.id}')
        
        logger.info(f"New comment added to post: {post.title}")

# Chat Signals
@receiver(post_save, sender=Message)
def process_chat_message(sender, instance, created, **kwargs):
    """Process new chat messages."""
    if created:
        conversation = instance.conversation
        
        # Update conversation's last activity
        conversation.updated_at = timezone.now()
        conversation.save()
        
        # Create chat metrics
        if instance.message_type == 'BOT':
            # Calculate response time
            try:
                last_user_message = conversation.messages.filter(
                    message_type='USER'
                ).latest('created_at')
                
                response_time = (instance.created_at - last_user_message.created_at).total_seconds()
                
                ChatMetric.objects.create(
                    conversation=conversation,
                    response_time=response_time,
                    conversation_length=conversation.messages.count()
                )
            except Message.DoesNotExist:
                pass
        
        # Invalidate caches
        cache.delete(f'conversation_{conversation.id}')
        cache.delete(f'user_conversations_{conversation.user.id}')
        
        logger.info(f"Processed chat message in conversation {conversation.id}")

# Cleanup Signals
@receiver(post_delete, sender=Post)
def cleanup_post(sender, instance, **kwargs):
    """Clean up after post deletion."""
    # Clear caches
    cache.delete(f'post_{instance.slug}')
    cache.delete('blog_posts_list')
    
    logger.info(f"Cleaned up deleted post: {instance.title}")

@receiver(post_delete, sender=User)
def cleanup_user(sender, instance, **kwargs):
    """Clean up after user deletion."""
    # Clear caches
    cache.delete(f'user_profile_{instance.id}')
    cache.delete(f'user_tests_{instance.id}')
    
    logger.info(f"Cleaned up deleted user: {instance.email}")

# Error Handling
def signal_error_handler(func):
    """Decorator to handle signal errors."""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.error(f"Signal error in {func.__name__}: {str(e)}")
    return wrapper

# Apply error handling to all signal handlers
create_user_profile = signal_error_handler(create_user_profile)
invalidate_user_cache = signal_error_handler(invalidate_user_cache)
process_test_result = signal_error_handler(process_test_result)
prepare_post = signal_error_handler(prepare_post)
handle_post_save = signal_error_handler(handle_post_save)
handle_comment_save = signal_error_handler(handle_comment_save)
process_chat_message = signal_error_handler(process_chat_message)
cleanup_post = signal_error_handler(cleanup_post)
cleanup_user = signal_error_handler(cleanup_user)
