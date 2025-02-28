from rest_framework import serializers
from django.utils.text import slugify
from .models import Category, Tag, Post, Comment, Like, Newsletter
from users.serializers import UserSerializer

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'name', 'slug', 'description')
        read_only_fields = ('slug',)

    def create(self, validated_data):
        validated_data['slug'] = slugify(validated_data['name'])
        return super().create(validated_data)

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'slug')
        read_only_fields = ('slug',)

    def create(self, validated_data):
        validated_data['slug'] = slugify(validated_data['name'])
        return super().create(validated_data)

class CommentSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    replies = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ('id', 'author', 'content', 'created_at', 'updated_at', 'replies')
        read_only_fields = ('author', 'replies')

    def get_replies(self, obj):
        if obj.replies.exists():
            return CommentSerializer(obj.replies.filter(is_approved=True), many=True).data
        return []

class PostListSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    category = CategorySerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    likes_count = serializers.IntegerField(read_only=True)
    is_liked = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = (
            'id', 'title', 'slug', 'author', 'excerpt', 'featured_image',
            'category', 'tags', 'published_at', 'read_time',
            'likes_count', 'is_liked'
        )
        read_only_fields = ('slug', 'likes_count')

    def get_is_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Like.objects.filter(user=request.user, post=obj).exists()
        return False

class PostDetailSerializer(PostListSerializer):
    comments = serializers.SerializerMethodField()
    
    class Meta(PostListSerializer.Meta):
        fields = PostListSerializer.Meta.fields + ('content', 'comments', 'views_count')

    def get_comments(self, obj):
        return CommentSerializer(
            obj.comments.filter(parent=None, is_approved=True),
            many=True
        ).data

class PostCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = (
            'title', 'content', 'excerpt', 'featured_image',
            'category', 'tags', 'status'
        )

    def create(self, validated_data):
        validated_data['slug'] = slugify(validated_data['title'])
        validated_data['author'] = self.context['request'].user
        return super().create(validated_data)

class CommentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ('content', 'parent')

    def create(self, validated_data):
        validated_data['author'] = self.context['request'].user
        validated_data['post'] = self.context['post']
        return super().create(validated_data)

class NewsletterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Newsletter
        fields = ('email',)

    def validate_email(self, value):
        if Newsletter.objects.filter(email=value, is_active=True).exists():
            raise serializers.ValidationError("This email is already subscribed.")
        return value

class PostAnalyticsSerializer(serializers.Serializer):
    total_views = serializers.IntegerField()
    total_likes = serializers.IntegerField()
    total_comments = serializers.IntegerField()
    engagement_rate = serializers.FloatField()
    top_posts = PostListSerializer(many=True)

class EngagementAnalyticsSerializer(serializers.Serializer):
    daily_views = serializers.DictField()
    daily_likes = serializers.DictField()
    daily_comments = serializers.DictField()
    user_engagement = serializers.DictField()
