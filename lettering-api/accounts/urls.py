from django.urls import path
from . import views

urlpatterns = [
    path('nickname/check/', views.NicknameCheckView.as_view(), name='nickname_check'),
]