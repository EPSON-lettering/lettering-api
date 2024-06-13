from drf_yasg.utils import swagger_auto_schema
from rest_framework.views import APIView
from .serializers import *
import requests
from django.conf import settings
from rest_framework.response import Response
from rest_framework import status
from .models import User, Language, OauthUser
from .serializers import UserSerializer

# 구글 소셜로그인 변수 설정
BASE_URL = 'http://localhost:8000/'
GOOGLE_CALLBACK_URI = BASE_URL + 'account/google/callback/'

class NicknameCheckView(APIView):

    @swagger_auto_schema(operation_summary="nickname 중복 확인", request_body=NicknameCheckSerializer)
    def post(self, request):
        serializer = NicknameCheckSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        is_unique = not User.objects.filter(nickname=serializer.validated_data['nickname']).exists()
        return Response({"isUnique": is_unique})

class GoogleLogin(APIView):
    def get(self, request):
        google_oauth_url = (
            f"https://accounts.google.com/o/oauth2/v2/auth?client_id={settings.GOOGLE_CLIENT_ID}"
            f"&redirect_uri={GOOGLE_CALLBACK_URI}"
            f"&scope=email"
            f"&response_type=code"
        )
        return Response({"oauth_url": google_oauth_url})

class GoogleCallback(APIView):
    def get(self, request):
        code = request.GET.get('code')
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
        profile_image_url = email_data.get('picture')
        provider_id = email_data.get('id')

        try:
            oauth_user = OauthUser.objects.get(provider='google', provider_id=provider_id)
            user = User.objects.get(oauth_id=oauth_user)
            user.is_loggined = True
            user.save()
            serializer = UserSerializer(user)
            return Response({'message': 'User logged in successfully', 'user': serializer.data}, status=status.HTTP_200_OK)
        except OauthUser.DoesNotExist:
            return Response({'email': email, 'profile_image_url': profile_image_url, 'provider_id': provider_id, 'message': 'User does not exist. Please choose a language to register.'}, status=status.HTTP_200_OK)

class LanguageSelection(APIView):
    def post(self, request):
        email = request.data.get('email')
        if not email:
            return Response({'error': 'Email not found in request'}, status=status.HTTP_400_BAD_REQUEST)

        language_id = request.data.get('language_id')
        if not language_id:
            return Response({'error': 'No language selected'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            language = Language.objects.get(id=language_id)
        except Language.DoesNotExist:
            return Response({'error': 'Invalid language selected'}, status=status.HTTP_400_BAD_REQUEST)

        return Response({'message': 'Language selected. Please choose a nickname.', 'language_id': language.id}, status=status.HTTP_200_OK)

class NicknameSelection(APIView):
    def post(self, request):
        email = request.data.get('email')
        if not email:
            return Response({'error': 'Email not found in request'}, status=status.HTTP_400_BAD_REQUEST)

        language_id = request.data.get('language_id')
        if not language_id:
            return Response({'error': 'Language not found in request'}, status=status.HTTP_400_BAD_REQUEST)

        provider_id = request.data.get('provider_id')
        if not provider_id:
            return Response({'error': 'Provider ID not found in request'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = NicknameSerializer(data=request.data)
        if serializer.is_valid():
            nickname = serializer.validated_data['nickname']
            language = Language.objects.get(id=language_id)
            profile_image_url = request.data.get('profile_image_url')

            oauth_user, created = OauthUser.objects.get_or_create(provider='google', provider_id=provider_id)
            user = User.objects.create(
                oauth_id=oauth_user,
                email=email,
                nickname=nickname,
                language=language,
                profile_image_url=profile_image_url
            )

            serializer = UserSerializer(user)
            return Response({'message': 'User registered successfully', 'user': serializer.data}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
