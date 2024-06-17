from django.urls import path, re_path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from django.urls import path
from .views import *
from rest_framework.permissions import AllowAny

from . import views

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
    re_path('swagger(?P<format>\.json|\.yaml)$',schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),

    path('google/login/', GoogleLogin.as_view(), name='google_login'),
    path('google/oauth/', GoogleLogin.as_view(), name='google_oauth_login_url'),
    path('google/callback/', GoogleCallback.as_view(), name='google_callback'),
    path('register/', RegisterUser.as_view(), name='register_user'),
    path('logout/', Logout.as_view(), name='logout'),
    path('user/details/', UserDetails.as_view(), name='user_info'),
    path('languages/', LanguageListView.as_view(), name='language_list'),
    path('nickname/', views.NicknameView.as_view(), name='nickname'),
    path('match/check/', views.CheckUserHasMatchView.as_view(), name='check user has match')
]
