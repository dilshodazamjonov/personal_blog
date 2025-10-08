from rest_framework import viewsets, status, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import (
    IsAuthenticated, AllowAny, IsAuthenticatedOrReadOnly, IsAdminUser
)
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import Post, User, Category
from .serializers import (
    UserSerializer,
    PostListSerializer,
    PostDetailSerializer,
    PostCreateUpdateSerializer,
    CommentSerializer,
    CategorySerializer,
)

# =============================================================
# AUTH & USER VIEWS
# =============================================================

class RegisterView(generics.CreateAPIView):
    """Register a new user"""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Add extra fields into JWT payload"""

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['username'] = user.username
        token['email'] = user.email
        token['is_staff'] = user.is_staff
        return token


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


# =============================================================
# USER VIEWSET
# =============================================================

class UserViewSet(viewsets.ModelViewSet):
    """
    Admins: full CRUD on all users
    Authenticated users: view or edit their own profile
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer

    def get_permissions(self):
        if self.action in ['list', 'destroy']:
            permission_classes = [IsAdminUser]
        elif self.action in ['retrieve', 'update', 'partial_update']:
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [AllowAny]
        return [perm() for perm in permission_classes]

    def get_queryset(self):
        """Users can see all if admin, else only themselves"""
        user = self.request.user
        if user.is_staff:
            return User.objects.all()
        return User.objects.filter(id=user.pk)


# =============================================================
# CATEGORY VIEWSET
# =============================================================

class CategoryViewSet(viewsets.ModelViewSet):
    """
    CRUD for blog categories.
    Anyone can list, only admin can create/update/delete.
    """
    queryset = Category.objects.all().order_by('name')
    serializer_class = CategorySerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminUser()]
        return [AllowAny()]


# =============================================================
# POST VIEWSET
# =============================================================

class PostViewSet(viewsets.ModelViewSet):
    """
    Handles all Post CRUD + custom actions (like, comment, save)
    """
    queryset = (
        Post.objects.all()
        .select_related('author', 'category')
        .prefetch_related('comments', 'liked_by', 'saved_by')
        .order_by('-created_at')
    )
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_serializer_class(self):
        """Dynamically select serializer depending on the action"""
        if self.action == 'list':
            return PostListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return PostCreateUpdateSerializer
        return PostDetailSerializer

    def perform_create(self, serializer):
        """Set post author automatically"""
        serializer.save(author=self.request.user)

    # -----------------------------
    # CUSTOM ACTIONS
    # -----------------------------
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def comment(self, request, pk=None):
        """Add a comment to a post"""
        post = self.get_object()
        serializer = CommentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(author=request.user, post=post)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def like(self, request, pk=None):
        """Toggle like/unlike for a post"""
        post = self.get_object()
        user = request.user

        if user in post.liked_by.all():
            post.liked_by.remove(user)
            post.likes = max(post.likes - 1, 0)
            message = "Unliked"
        else:
            post.liked_by.add(user)
            post.likes += 1
            message = "Liked"

        post.save(update_fields=['likes'])
        return Response({'message': message, 'likes': post.likes}, status=200)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def save_post(self, request, pk=None):
        """Toggle save/unsave for a post"""
        post = self.get_object()
        user = request.user

        if post in user.saved_posts.all():
            user.saved_posts.remove(post)
            message = "Post unsaved"
        else:
            user.saved_posts.add(post)
            message = "Post saved"

        return Response({'message': message}, status=200)

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def saved(self, request):
        """Return all posts saved by the logged-in user"""
        user = request.user
        saved_posts = user.saved_posts.all().select_related('author').prefetch_related('comments')
        serializer = PostListSerializer(saved_posts, many=True)
        return Response(serializer.data)
