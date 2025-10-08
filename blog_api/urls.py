from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.views import TokenRefreshView
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

from blog.views import RegisterView, CustomTokenObtainPairView


# ------------------------------------------------------------
# Swagger Schema View
# ------------------------------------------------------------
schema_view = get_schema_view(
    openapi.Info(
        title="Blog API",
        default_version='v1',
        description="Vue Blog backend with JWT authentication",
        contact=openapi.Contact(email="support@yourblog.com"),
    ),
    public=True,
    permission_classes=[AllowAny],
)


# ------------------------------------------------------------
# URL Patterns
# ------------------------------------------------------------
urlpatterns = [
    path('admin/', admin.site.urls),

    # 🔐 Auth endpoints
    path('api/auth/register/', RegisterView.as_view(), name='register'),
    path('api/auth/login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # 📝 Blog app endpoints
    path('api/', include('blog.urls')),

    # 📄 Swagger Docs
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='swagger-ui'),
]


# ------------------------------------------------------------
# Serve media files in development
# ------------------------------------------------------------
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
