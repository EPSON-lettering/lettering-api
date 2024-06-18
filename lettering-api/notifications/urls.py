from django.urls import path, re_path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework.permissions import AllowAny
from .views import NotificationAPIView

schema_view = get_schema_view(
    openapi.Info(
        title="Lettering API",
        default_version='v1',
        description="Lettering API",
    ),
    public=True,
    permission_classes=([AllowAny]),
)

urlpatterns = [
    path('notifications/', NotificationAPIView.as_view(), name='notification_list'),
    path('notifications/<int:notification_id>/read/', NotificationAPIView.as_view(), name='notification_read'),
    path('notifications/<int:notification_id>/', NotificationAPIView.as_view(), name='notification_delete'),

    re_path('swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]
