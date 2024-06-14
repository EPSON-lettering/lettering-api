from drf_yasg.utils import swagger_auto_schema
from rest_framework.views import APIView
from .serializers import *
import requests
from django.conf import settings
from rest_framework.response import Response
from rest_framework import status
from .models import User, Language
from oauth.models import OauthUser
from .serializers import UserSerializer
import jwt

# 구글 소셜로그인 변수 설정
BASE_URL = 'http://localhost:8000/'
GOOGLE_CALLBACK_URI = BASE_URL + 'account/google/callback/'

class NicknameCheckView(APIView):

    @swagger_auto_schema(operation_summary="Nickname 중복 확인", request_body=NicknameCheckSerializer)
    def post(self, request):
        serializer = NicknameCheckSerializer(data=request.data)
        if serializer.is_valid():
            return Response({"isUnique": True}, status=status.HTTP_200_OK)
        return Response({"isUnique": False, "errors": serializer.errors}, status=status.HTTP_200_OK)


class GoogleLogin(APIView):
    @swagger_auto_schema(operation_summary="Google OAuth 로그인")
    def get(self, request):
        google_oauth_url = (
            f"https://accounts.google.com/o/oauth2/v2/auth?client_id={settings.GOOGLE_CLIENT_ID}"
            f"&redirect_uri={GOOGLE_CALLBACK_URI}"
            f"&scope=email"
            f"&response_type=code"
        )
        return Response({"oauth_url": google_oauth_url})


class GoogleAuthLoginUrl(APIView):
    @swagger_auto_schema(operation_summary="Google OAuth 로그인")
    def get(self, request):
        google_oauth_url = (
            f"https://accounts.google.com/o/oauth2/v2/auth?client_id={settings.GOOGLE_CLIENT_ID}"
            f"&redirect_uri={GOOGLE_CALLBACK_URI}"
            f"&scope=email"
            f"&response_type=code"
        )
        return Response({"oauth_url": google_oauth_url})


class GoogleCallback(APIView):
    @swagger_auto_schema(operation_summary="Google OAuth Callback", request_body=GoogleCallbackSerializer)
    def post(self, request):
        code = request.data.get('code')
        if not code:
            return Response({'error': 'No code provided'}, status=status.HTTP_400_BAD_REQUEST)

        token_url = 'https://oauth2.googleapis.com/token'
        token_params = {
            'client_id': settings.GOOGLE_CLIENT_ID,
            'client_secret': settings.GOOGLE_CLIENT_SECRET,
            'code': code,
            'redirect_uri': GOOGLE_CALLBACK_URI,
            'grant_type': 'authorization_code',
        }
        token_req = requests.post(token_url, data=token_params)
        token_data = token_req.json()
        if 'error' in token_data:
            return Response({'error': token_data['error']}, status=status.HTTP_400_BAD_REQUEST)

        access_token = token_data.get('access_token')

        email_url = 'https://www.googleapis.com/oauth2/v1/userinfo'
        email_req = requests.get(email_url, params={'access_token': access_token})
        email_data = email_req.json()
        if 'error' in email_data:
            return Response({'error': email_data['error']}, status=status.HTTP_400_BAD_REQUEST)

        email = email_data.get('email')
        provider_id = email_data.get('id')

        try:
            oauth_user = OauthUser.objects.get(provider='google', provider_id=provider_id)
            user = User.objects.get(oauth_id=oauth_user)
            user.is_loggined = True
            user.save()

            payload = {'user_id': user.id}
            jwt_token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')
            serializer = UserSerializer(user)
            return Response({'message': 'User logged in successfully', 'user': serializer.data, 'token': jwt_token}, status=status.HTTP_200_OK)
        except OauthUser.DoesNotExist:
            return Response({
                'unique': email,
                'provider': 'google',
                'message': 'User does not exist. Please proceed with registration.'
            }, status=status.HTTP_200_OK)


class RegisterUser(APIView):
    @swagger_auto_schema(operation_summary="회원가입", request_body=RegisterUserSerializer)
    def post(self, request):
        serializer = RegisterUserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()

            payload = {'user_id': user.id}
            jwt_token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')
            return Response({'message': 'User registered successfully', 'user': UserSerializer(user).data, 'token': jwt_token}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class Logout(APIView):
    @swagger_auto_schema(operation_summary="로그아웃")
    def post(self, request):
        request.session.flush()
        return Response({'message': 'User logged out successfully'}, status=status.HTTP_200_OK)


class LanguageListView(APIView):
    @swagger_auto_schema(operation_summary="언어 List")
    def get(self, request):
        languages = Language.objects.all()
        serializer = LanguageSerializer(languages, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
