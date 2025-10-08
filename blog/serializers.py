from rest_framework import serializers
from .models import User, Category, Post, Comment


# -----------------------------
# CATEGORY SERIALIZER
# -----------------------------
class CategorySerializer(serializers.ModelSerializer):
    post_count = serializers.IntegerField(source='posts.count', read_only=True)

    class Meta:
        model = Category
        fields = ['id', 'name', 'post_count']


# -----------------------------
# USER SERIALIZER
# -----------------------------
class UserSerializer(serializers.ModelSerializer):
    post_count = serializers.IntegerField(source='posts.count', read_only=True)
    comment_count = serializers.IntegerField(source='comments.count', read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'post_count', 'comment_count']




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
    categories = serializers.StringRelatedField(many=True)
    comment_count = serializers.IntegerField(source='comments.count', read_only=True)

    class Meta:
        model = Post
        fields = [
            'id',
            'title',
            'author_username',
            'categories',
            'comment_count',
            'created_at',
        ]


# -----------------------------
# POST SERIALIZER (Detailed View)
# -----------------------------
class PostDetailSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    categories = CategorySerializer(many=True, read_only=True)
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
            'categories',
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
        fields = ['title', 'content', 'categories']

    def create(self, validated_data):
        request = self.context.get('request')
        post = Post.objects.create(author=request.user, **validated_data) # type: ignore
        return post

    def update(self, instance, validated_data):
        instance.title = validated_data.get('title', instance.title)
        instance.content = validated_data.get('content', instance.content)
        if 'categories' in validated_data:
            instance.categories.set(validated_data['categories'])
        instance.save()
        return instance
