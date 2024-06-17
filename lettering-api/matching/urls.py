from .views import (
    MatchView,
    MatchRequestView,
    GetMatchDetailsView,
    GetMatchingListView,
    QuestionView,
    CurrentQuestionView,
)
from django.urls import path, re_path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from django.urls import path
from rest_framework.permissions import AllowAny

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
    path('', MatchView.as_view(), name='match'),
    path('request/<int:request_id>/<str:action>/', MatchRequestView.as_view(), name='match_request_action'),
    path('details/', GetMatchDetailsView.as_view()),
    path('list/', GetMatchingListView.as_view()),
    path('question/<int:match_id>/', QuestionView.as_view(), name='provide_random_question'),
    path('current/<int:match_id>/', CurrentQuestionView.as_view(), name='current-question'),

    re_path('swagger(?P<format>\.json|\.yaml)$',schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]
