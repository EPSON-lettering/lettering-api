from django.urls import path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view

from .views import UserBadgeAPIView, BadgeAPIView, PartnerBadgeAPIView

schema_view = get_schema_view(
    openapi.Info(
        title="Lettering API",
        default_version='v1',
        description="Lettering API",
    ),
    public=True,
)

urlpatterns = [
    path('',UserBadgeAPIView.as_view() , name='badges'),
    path('all/',BadgeAPIView.as_view(), name='badges'),
    path('partner/', PartnerBadgeAPIView.as_view(), name='badges'),
]