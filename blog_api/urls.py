from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenRefreshView
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework.permissions import AllowAny
from blog.views import RegisterView, CustomTokenObtainPairView  # ✅ your single app

schema_view = get_schema_view(
    openapi.Info(
        title="Blog API",
        default_version='v1',
        description="Vue Blog backend with JWT authentication",
    ),
    public=True,
    permission_classes=[AllowAny],
)

urlpatterns = [
    path('admin/', admin.site.urls),

    # 🔐 Auth
    path('api/register/', RegisterView.as_view(), name='register'),
    path('api/login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # 📝 Blog endpoints
    path('api/', include('blog.urls')),

    # 📄 Swagger Docs
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='swagger-ui'),
]
