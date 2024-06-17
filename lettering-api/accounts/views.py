from drf_yasg.utils import swagger_auto_schema
from rest_framework.views import APIView
from .serializers import *
import requests
from django.conf import settings
from rest_framework.response import Response
from rest_framework import status
from .models import User, Language
from django.db.models import Q
from matching.models import Match
from oauth.models import OauthUser
from interests.models import UserInterest, Interest
from .serializers import UserSerializer
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from drf_yasg import openapi

# 구글 소셜로그인 변수 설정
BASE_URL = settings.BASE_URL
GOOGLE_CALLBACK_URI = BASE_URL + settings.GOOGLE_CALLBACK_URI


class NicknameView(APIView):
    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        elif self.request.method == 'POST':
            return [IsAuthenticated()]
        return super().get_permissions()

    @swagger_auto_schema(
        operation_summary="닉네임 유효성 검사",
        query_serializer=NicknameCheckSerializer(),
        responses={200: "available: boolean, error: string"}
    )
    def get(self, request):
        serializer = NicknameCheckSerializer(data=request.query_params)
        if serializer.is_valid():
            return Response({"available": True}, status=status.HTTP_200_OK)
        return Response({"available": False, "error": serializer.errors['nickname'][0]}, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_summary="닉네임 변경",
        request_body=NicknameCheckSerializer,
        responses={200: "Success", 400: "Error message"}
    )
    def post(self, request):
        serializer = NicknameCheckSerializer(data=request.data)
        if serializer.is_valid():
            nickname = serializer.validated_data['nickname']
            user = request.user
            if user.nickname == nickname:
                return Response(status=status.HTTP_200_OK)
            user.nickname = nickname
            user.save()
            return Response(status=status.HTTP_200_OK)
        return Response({"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class GoogleLogin(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_summary="Google OAuth 로그인",
        responses={200: "oauthUrl: string"}
    )
    def get(self, request):
        google_oauth_url = (
            f"https://accounts.google.com/o/oauth2/v2/auth?client_id={settings.GOOGLE_CLIENT_ID}"
            f"&redirect_uri={GOOGLE_CALLBACK_URI}"
            f"&scope=email"
            f"&response_type=code"
        )
        return Response({"oauthUrl": google_oauth_url})


class GoogleCallback(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_summary="Google OAuth Callback",
        request_body=GoogleCallbackSerializer,
        responses={
            200: "message: string, user: object, access: string, refresh: string",
            400: "Error message",
            401: "unique: string, provider: string, message: string"
        }
    )
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
            oauth_user = OauthUser.objects.get(provider='google', provider_id=email)
            user = User.objects.get(oauth=oauth_user)
            user.is_loggined = True
            user.save()
            user_interests = UserInterest.objects.filter(user=user)
            interests = [user_interest.interest for user_interest in user_interests]

            refresh = RefreshToken.for_user(user)
            serializer = UserSerializer(user, interests=interests)
            user_serial = serializer.data
            return Response({
                'message': '로그인 성공',
                'user': user_serial,
                'access': str(refresh.access_token),
                'refresh': str(refresh)
            }, status=status.HTTP_200_OK)
        except OauthUser.DoesNotExist:
            return Response({
                'unique': email,
                'provider': 'google',
                'message': '이메일에 해당하는 유저가 존재하지 않습니다. 회원가입을 진행해주세요.'
            }, status=status.HTTP_401_UNAUTHORIZED)


class RegisterUser(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_summary="회원가입",
        request_body=RegisterUserSerializer,
        responses={
            201: "user: object, access: string, refresh: string",
            400: "Error message"
        }
    )
    def post(self, request):
        serializer = RegisterUserSerializer(data=request.data)
        if serializer.is_valid():
            user, interests = serializer.save()

            refresh = RefreshToken.for_user(user)
            return Response({
                'user': UserSerializer(user, interests=interests).data,
                'access': str(refresh.access_token),
                'refresh': str(refresh)
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class Logout(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="로그아웃",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'refresh': openapi.Schema(type=openapi.TYPE_STRING)
            },
            required=['refresh']
        ),
        responses={205: "Success", 400: "Error message"}
    )
    def post(self, request):
        try:
            refresh_token = request.data.get('refresh')
            token = RefreshToken(refresh_token)
            token.blacklist()

            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class LanguageListView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_summary="언어 List",
        responses={200: LanguageSerializer(many=True)}
    )
    def get(self, request):
        languages = Language.objects.all()
        serializer = LanguageSerializer(languages, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class UserDetails(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="사용자 정보 불러오기",
        responses={200: UserSerializer()}
    )
    def get(self, request):
        user_interests = UserInterest.objects.filter(user=request.user)
        interests = [user_interest.interest for user_interest in user_interests]
        serializers = UserSerializer(request.user, interests=interests)

        return Response(serializers.data, status=status.HTTP_200_OK)


class CheckUserHasMatchView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="사용자 매칭 상태 조회",
        responses={200: MatchStatusSerializer()}
    )
    def get(self, req):
        user = req.user
        match = Match.objects.filter(
            Q(requester=user) | Q(acceptor=user) & Q(withdraw_reason__isnull=True)
        )
        print(f'match: {match}')
        if match.exists() is False:
            return Response({"isMatch": False})
        return Response({"isMatch": True})
