from django.urls import path, re_path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions
from rest_framework.permissions import AllowAny

from .views import EpsonPrintConnectAPI, ScannerDestinationsView, FileUploadView, EpsonConnectEmailAPIView, \
    ToEpsonFileUploadView, EpsonLetterIdPrintConnectAPI

schema_view = get_schema_view(
    openapi.Info(
        title="Lettering API",
        default_version='v1',
        description="Lettering API",
    ),
    public=True,
    permission_classes=(AllowAny,),
)

urlpatterns = [
    re_path('swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('prints/<int:letter_id>', EpsonLetterIdPrintConnectAPI.as_view(),name='epson-print-letter'),
    path('prints', EpsonPrintConnectAPI.as_view(),name='epson-connect-api'),
    path('prints/auth',EpsonConnectEmailAPIView.as_view(),name='epson-email-auth'),
    path('scan', ScannerDestinationsView.as_view(),name='epson-scan-api'),
    path('scan/fileSave/<str:username>', ToEpsonFileUploadView.as_view(), name='epson-file-upload'),
    path('scan/fileSave', FileUploadView.as_view(), name='epson-file-upload-with-files'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]