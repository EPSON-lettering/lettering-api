from django.urls import path, re_path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions
from django.urls import path
from .views import *

from . import views

schema_view = get_schema_view(
    openapi.Info(
        title="Lettering API",
        default_version='v1',
        description="Lettering API",
    ),
    public=True,
)

urlpatterns = [
    path('nickname/check/', views.NicknameCheckView.as_view(), name='nickname_check'),
    re_path('swagger(?P<format>\.json|\.yaml)$',schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),

    path('google/login/', GoogleLogin.as_view(), name='google_login'),
    path('google/callback/', GoogleCallback.as_view(), name='google_callback'),
    path('language-selection/', LanguageSelection.as_view(), name='language_selection'),
    path('nickname-selection/', NicknameSelection.as_view(), name='nickname_selection'),
]