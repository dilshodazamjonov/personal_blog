from rest_framework import serializers
from .models import User, Category, Post, Comment


# -----------------------------
# CATEGORY SERIALIZER
# -----------------------------
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']

# -----------------------------
# USER SERIALIZER
# -----------------------------
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'avatar', 'bio']

# -----------------------------
# COMMENT SERIALIZER
# -----------------------------
class CommentSerializer(serializers.ModelSerializer):
    author_username = serializers.CharField(source='author.username', read_only=True)
    post_title = serializers.CharField(source='post.title', read_only=True)

    class Meta:
        model = Comment
        fields = [
            'id',
            'author',
            'author_username',
            'post',
            'post_title',
            'text',
            'created_at',
        ]
        read_only_fields = ['author', 'created_at']


# -----------------------------
# POST SERIALIZER (List View)
# -----------------------------
class PostListSerializer(serializers.ModelSerializer):
    author_username = serializers.CharField(source='author.username', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    comment_count = serializers.IntegerField(source='comments.count', read_only=True)

    class Meta:
        model = Post
        fields = [
            'id',
            'title',
            'author_username',
            'category_name',
            'comment_count',
            'created_at',
        ]


# -----------------------------
# POST SERIALIZER (Detailed View)
# -----------------------------
class PostDetailSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    category = CategorySerializer(read_only=True)
    comments = CommentSerializer(many=True, read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    time_since_created = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = [
            'id',
            'title',
            'content',
            'author',
            'category',
            'comments',
            'created_at',
            'time_since_created',
        ]
        read_only_fields = ['author', 'created_at']

    def get_time_since_created(self, obj):
        from django.utils.timesince import timesince
        return timesince(obj.created_at) + " ago"


# -----------------------------
# POST CREATE / UPDATE SERIALIZER
# -----------------------------
class PostCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ['title', 'content', 'category']

    def create(self, validated_data):
        return Post.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.title = validated_data.get('title', instance.title)
        instance.content = validated_data.get('content', instance.content)
        if 'category' in validated_data:
            instance.category = validated_data['category']
        instance.save()
        return instance
