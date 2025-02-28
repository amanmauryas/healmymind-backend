from rest_framework import serializers
from .models import Conversation, Message, SupportResource, ChatFeedback, ChatMetric
from users.serializers import UserSerializer

class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ('id', 'content', 'message_type', 'created_at', 'metadata')
        read_only_fields = ('created_at',)

class ConversationListSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    last_message = serializers.SerializerMethodField()
    
    class Meta:
        model = Conversation
        fields = ('id', 'user', 'title', 'created_at', 'updated_at', 'last_message', 'metadata')
        read_only_fields = ('created_at', 'updated_at')

    def get_last_message(self, obj):
        last_message = obj.messages.last()
        if last_message:
            return MessageSerializer(last_message).data
        return None

class ConversationDetailSerializer(ConversationListSerializer):
    messages = MessageSerializer(many=True, read_only=True)
    
    class Meta(ConversationListSerializer.Meta):
        fields = ConversationListSerializer.Meta.fields + ('messages',)

class SendMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ('content', 'metadata')

    def create(self, validated_data):
        validated_data['conversation'] = self.context['conversation']
        validated_data['message_type'] = 'USER'
        return super().create(validated_data)

class SupportResourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = SupportResource
        fields = (
            'id', 'title', 'description', 'resource_type',
            'url', 'phone_number', 'is_emergency', 'order'
        )

class ChatFeedbackSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = ChatFeedback
        fields = ('id', 'conversation', 'user', 'feedback_type', 'comment', 'created_at')
        read_only_fields = ('user', 'created_at')

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

class ChatMetricSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatMetric
        fields = (
            'conversation', 'response_time', 'user_satisfaction',
            'conversation_length', 'created_at', 'metadata'
        )
        read_only_fields = ('created_at',)

class ChatAnalyticsSerializer(serializers.Serializer):
    total_conversations = serializers.IntegerField()
    active_conversations = serializers.IntegerField()
    avg_response_time = serializers.FloatField()
    avg_satisfaction = serializers.FloatField()
    conversation_trends = serializers.DictField()

class FeedbackAnalyticsSerializer(serializers.Serializer):
    feedback_distribution = serializers.DictField()
    satisfaction_trend = serializers.DictField()
    common_issues = serializers.ListField()
    improvement_areas = serializers.ListField()

class ResponseTimeAnalyticsSerializer(serializers.Serializer):
    avg_response_time = serializers.FloatField()
    response_time_distribution = serializers.DictField()
    peak_hours = serializers.DictField()
    bottlenecks = serializers.ListField()

class SentimentAnalysisSerializer(serializers.Serializer):
    sentiment_score = serializers.FloatField()
    sentiment_label = serializers.CharField()
    confidence = serializers.FloatField()
    key_phrases = serializers.ListField()
    entities = serializers.DictField()

class ResourceSuggestionSerializer(serializers.Serializer):
    conversation_id = serializers.IntegerField()
    user_message = serializers.CharField()
    suggested_resources = SupportResourceSerializer(many=True)
    confidence_scores = serializers.DictField()
    context = serializers.DictField()

class AdminConversationSerializer(ConversationDetailSerializer):
    metrics = ChatMetricSerializer(many=True, read_only=True)
    feedback = ChatFeedbackSerializer(many=True, read_only=True)
    
    class Meta(ConversationDetailSerializer.Meta):
        fields = ConversationDetailSerializer.Meta.fields + ('metrics', 'feedback')
