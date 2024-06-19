from django.urls import path, include
from .views import LetterAPIView, CheckUserLetterAPIView, CheckOtherPersonAPIView

urlpatterns = [
    path('lettering/', LetterAPIView.as_view(), name='letters'),
    path('otherPerson/lettering', CheckOtherPersonAPIView.as_view(), name='receive letters'),
    path('user/lettering', CheckUserLetterAPIView.as_view(), name='check user letters'),
]