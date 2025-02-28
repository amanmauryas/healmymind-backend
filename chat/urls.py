from django.urls import path
from . import views

urlpatterns = [
    # Conversation management
    path('conversations/', views.ConversationListView.as_view(), name='conversation-list'),
    path('conversations/create/', views.ConversationCreateView.as_view(), name='conversation-create'),
    path('conversations/<int:pk>/', views.ConversationDetailView.as_view(), name='conversation-detail'),
    path('conversations/<int:pk>/messages/', views.MessageListView.as_view(), name='message-list'),
    path('conversations/<int:pk>/send/', views.SendMessageView.as_view(), name='send-message'),
    
    # Support resources
    path('resources/', views.SupportResourceListView.as_view(), name='support-resources'),
    path('resources/<int:pk>/', views.SupportResourceDetailView.as_view(), name='resource-detail'),
    path('resources/emergency/', views.EmergencyResourcesView.as_view(), name='emergency-resources'),
    
    # Feedback and metrics
    path('conversations/<int:pk>/feedback/', views.ChatFeedbackView.as_view(), name='chat-feedback'),
    path('conversations/<int:pk>/metrics/', views.ChatMetricsView.as_view(), name='chat-metrics'),
    
    # Admin endpoints
    path('admin/conversations/', views.AdminConversationListView.as_view(), name='admin-conversation-list'),
    path('admin/conversations/<int:pk>/', views.AdminConversationDetailView.as_view(), name='admin-conversation-detail'),
    path('admin/resources/create/', views.AdminResourceCreateView.as_view(), name='admin-resource-create'),
    path('admin/resources/<int:pk>/update/', views.AdminResourceUpdateView.as_view(), name='admin-resource-update'),
    path('admin/resources/<int:pk>/delete/', views.AdminResourceDeleteView.as_view(), name='admin-resource-delete'),
    
    # Analytics
    path('analytics/usage/', views.ChatUsageAnalyticsView.as_view(), name='chat-usage-analytics'),
    path('analytics/feedback/', views.FeedbackAnalyticsView.as_view(), name='feedback-analytics'),
    path('analytics/response-times/', views.ResponseTimeAnalyticsView.as_view(), name='response-time-analytics'),
    
    # AI Integration
    path('analyze-sentiment/', views.AnalyzeSentimentView.as_view(), name='analyze-sentiment'),
    path('suggest-resources/', views.SuggestResourcesView.as_view(), name='suggest-resources'),
]
