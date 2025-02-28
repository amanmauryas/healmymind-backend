from django.db import models
from users.models import User

class Conversation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='conversations')
    title = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    metadata = models.JSONField(default=dict, blank=True)  # Store any additional conversation metadata

    class Meta:
        ordering = ['-updated_at']

    def __str__(self):
        return f"Conversation with {self.user.email} - {self.created_at}"

    def get_title(self):
        if self.title:
            return self.title
        # Get first message content as title if no title is set
        first_message = self.messages.first()
        if first_message:
            return first_message.content[:50] + "..."
        return f"Conversation {self.id}"

class Message(models.Model):
    MESSAGE_TYPES = [
        ('USER', 'User Message'),
        ('BOT', 'Bot Message'),
        ('SYSTEM', 'System Message'),
    ]

    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    content = models.TextField()
    message_type = models.CharField(max_length=10, choices=MESSAGE_TYPES)
    created_at = models.DateTimeField(auto_now_add=True)
    metadata = models.JSONField(default=dict, blank=True)  # Store message-specific metadata

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"{self.message_type} in {self.conversation} - {self.created_at}"

class SupportResource(models.Model):
    RESOURCE_TYPES = [
        ('CRISIS', 'Crisis Support'),
        ('THERAPY', 'Therapy Resources'),
        ('SELF_HELP', 'Self Help'),
        ('COMMUNITY', 'Community Support'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField()
    resource_type = models.CharField(max_length=20, choices=RESOURCE_TYPES)
    url = models.URLField(blank=True)
    phone_number = models.CharField(max_length=20, blank=True)
    is_emergency = models.BooleanField(default=False)
    order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order', 'title']

    def __str__(self):
        return self.title

class ChatFeedback(models.Model):
    FEEDBACK_TYPES = [
        ('HELPFUL', 'Helpful'),
        ('NOT_HELPFUL', 'Not Helpful'),
        ('INAPPROPRIATE', 'Inappropriate'),
        ('OTHER', 'Other'),
    ]

    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='feedback')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chat_feedback')
    feedback_type = models.CharField(max_length=20, choices=FEEDBACK_TYPES)
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Feedback from {self.user.email} - {self.feedback_type}"

class ChatMetric(models.Model):
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='metrics')
    response_time = models.FloatField(help_text="Response time in seconds")
    user_satisfaction = models.FloatField(null=True, blank=True)
    conversation_length = models.IntegerField(help_text="Number of messages in conversation")
    created_at = models.DateTimeField(auto_now_add=True)
    metadata = models.JSONField(default=dict, blank=True)

    def __str__(self):
        return f"Metrics for {self.conversation}"
