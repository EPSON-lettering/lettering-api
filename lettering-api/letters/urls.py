from django.urls import path, re_path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions
from rest_framework.permissions import AllowAny
from .views import (
    LetterAPIView,
    CheckUserLetterAPIView,
    CheckOtherPersonAPIView,
    LetterSendingAPI,
    LetterListAPI
)

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
    path('lettering/<int:scanDataId>', LetterAPIView.as_view(), name='lettering'),
    path('lettering/', LetterAPIView.as_view(), name='letters'),
    path('list/<int:user_id>', LetterListAPI.as_view(), name='get user letters'),
    path('otherPerson/lettering', CheckOtherPersonAPIView.as_view(), name='receive letters'),
    path('user/lettering', CheckUserLetterAPIView.as_view(), name='check user letters'),
    path('', LetterSendingAPI.as_view(), name="sending letter to matching opponent")
]
