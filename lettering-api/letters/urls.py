from django.urls import path, include
from .views import LetterAPIView


urlpatterns = [
    path('lettering/', LetterAPIView.as_view(), name='letters'),
]