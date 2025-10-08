from rest_framework.routers import DefaultRouter
from .views import PostViewSet, CategoryViewSet, UserViewSet

router = DefaultRouter()
router.register('posts', PostViewSet, basename='post')
router.register('categories', CategoryViewSet, basename='category')
router.register('users', UserViewSet, basename='user')

urlpatterns = router.urls