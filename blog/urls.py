from django.urls import path
from . import views

urlpatterns = [
    # Public endpoints
    path('posts/', views.PostListView.as_view(), name='post-list'),
    path('posts/<str:slug>/', views.PostDetailView.as_view(), name='post-detail'),
    path('categories/', views.CategoryListView.as_view(), name='category-list'),
    path('categories/<str:slug>/', views.CategoryPostsView.as_view(), name='category-posts'),
    path('tags/', views.TagListView.as_view(), name='tag-list'),
    path('tags/<str:slug>/', views.TagPostsView.as_view(), name='tag-posts'),
    
    # User interactions
    path('posts/<str:slug>/like/', views.PostLikeView.as_view(), name='post-like'),
    path('posts/<str:slug>/comments/', views.CommentListCreateView.as_view(), name='post-comments'),
    path('comments/<int:pk>/', views.CommentDetailView.as_view(), name='comment-detail'),
    path('comments/<int:pk>/reply/', views.CommentReplyView.as_view(), name='comment-reply'),
    
    # Newsletter
    path('newsletter/subscribe/', views.NewsletterSubscribeView.as_view(), name='newsletter-subscribe'),
    path('newsletter/unsubscribe/', views.NewsletterUnsubscribeView.as_view(), name='newsletter-unsubscribe'),
    
    # Admin endpoints
    path('admin/posts/', views.AdminPostListView.as_view(), name='admin-post-list'),
    path('admin/posts/create/', views.AdminPostCreateView.as_view(), name='admin-post-create'),
    path('admin/posts/<str:slug>/update/', views.AdminPostUpdateView.as_view(), name='admin-post-update'),
    path('admin/posts/<str:slug>/delete/', views.AdminPostDeleteView.as_view(), name='admin-post-delete'),
    path('admin/comments/', views.AdminCommentListView.as_view(), name='admin-comment-list'),
    path('admin/comments/<int:pk>/approve/', views.AdminCommentApproveView.as_view(), name='admin-comment-approve'),
    path('admin/comments/<int:pk>/delete/', views.AdminCommentDeleteView.as_view(), name='admin-comment-delete'),
    
    # Analytics
    path('analytics/posts/', views.PostAnalyticsView.as_view(), name='post-analytics'),
    path('analytics/engagement/', views.EngagementAnalyticsView.as_view(), name='engagement-analytics'),
]
