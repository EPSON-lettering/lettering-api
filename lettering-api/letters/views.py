from django.db.models import Q
from drf_yasg.utils import swagger_auto_schema
from rest_framework.parsers import JSONParser, FormParser, MultiPartParser
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from .models import Letter
from matching.models import Match
from accounts.domain import LetterWritingStatus
from accounts.models import User
from notifications.models import Notification
from .serializers import LetterSerializer, S3FileUploadSerializer, LetterModelSerializer
from drf_yasg import openapi


class CheckUserLetterAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="유저가 보낸편지 조회",
        responses={
            status.HTTP_200_OK : LetterSerializer(many=True),
        }
    )
    def get(self,reqeust):
        user = reqeust.user
        letters = Letter.objects.filter(sender=user).all().order_by('-created_at')[:3]
        serializer = LetterSerializer(letters, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CheckOtherPersonAPIView(APIView):
    permission_classes = [IsAuthenticated]
    @swagger_auto_schema(
        operation_summary="상대방 보낸편지 조회",
        responses={
            200: LetterSerializer(many=True)
        }
    )
    def get(self,request):
        user = request.user
        letters = Letter.objects.filter(receiver=user).all().order_by('-created_at')[:3]
        serializer = LetterSerializer(letters, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class LetterListAPI(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="유저 편지 리스트 조회",
        responses={
            200: LetterModelSerializer(many=True)
        }
    )
    def get(self, request, user_id: int):
        user = User.objects.get(id=user_id)
        letters = Letter.objects.filter(sender=user).all().order_by('-created_at')[:10]
        serializer = LetterModelSerializer(letters, user=user, many=True)
        return Response(serializer.data, status=200)


class LetterGetterAPI(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="유저 편지 리스트 조회",
        responses={
            200: LetterModelSerializer()
        }
    )
    def get(self, request, letter_id: int):
        letter = Letter.objects.get(id=letter_id)
        user = letter.sender
        serializer = LetterModelSerializer(letter, user=user)
        return Response(serializer.data, status=200)


class LetterAPIView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [JSONParser, FormParser, MultiPartParser]
    parser_classes = (MultiPartParser, FormParser)
    @swagger_auto_schema(
        operation_summary="서로 대화한 내역 조회",
        responses={200: LetterSerializer()}
    )
    def get(self, request):
        user = request.user
        letters = Letter.objects.filter(Q(sender=user) or Q(receiver=user) ).all().order_by('-created_at')
        serializer = LetterSerializer(letters, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_summary="편지 추가",
        request_body=LetterSerializer,
        responses={
            status.HTTP_201_CREATED: LetterSerializer,
            status.HTTP_400_BAD_REQUEST: 'Bad Request'
        }
    )
    def post(self, request):
        serializer = LetterSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            letter = serializer.save()
            Notification.objects.create(
                user=letter.receiver,
                letter=letter,
                message=f'{request.user.nickname} 님의 편지가 도착했습니다.',
                is_read=False,
                type='received'
            )
            self.award_badge(letter.sender, '편지의 제왕')
            self.check_consistent_writing(letter.sender)
            self.update_user_level(letter.sender)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def award_badge(self, user, badge_name):
        badge = Badge.objects.get(name=badge_name)
        user_badge, created = UserBadge.objects.get_or_create(
            user=user,
            badge=badge,
            defaults={'step': badge.steps.order_by('step_number').first(), 'progress': 0}
        )

        user_badge.progress += 1
        if user_badge.progress >= user_badge.step.required_count:
            next_step = badge.steps.filter(step_number=user_badge.step.step_number + 1).first()
            if next_step:
                user_badge.step = next_step
                user_badge.progress = 0
            else:
                user_badge.progress = user_badge.step.required_count
        user_badge.save()

    def check_consistent_writing(self, user):
        today = datetime.now().date()
        badge = Badge.objects.get(name='꾸준한 학습자')
        user_badge = UserBadge.objects.filter(user=user, badge=badge).first()

        if user_badge:
            current_step = user_badge.step
        else:
            current_step = badge.steps.order_by('step_number').first()

        required_days = current_step.required_count
        start_date = today - timedelta(days=required_days - 1)
        letters = Letter.objects.filter(sender=user, created_at__date__gte=start_date).order_by('created_at')

        if letters.exists():
            days = {letter.created_at.date() for letter in letters}
            if self.is_consecutive(days, required_days):
                self.award_badge(user, '꾸준한 학습자')
            else:
                if user_badge:
                    user_badge.progress = 0
                    user_badge.save()

    def is_consecutive(self, days, required_days):
        today = datetime.now().date()
        for i in range(required_days):
            if (today - timedelta(days=i)) not in days:
                return False
        return True

    def update_user_level(self, user):
        badges = UserBadge.objects.filter(user=user)
        if badges.exists():
            min_level = min(badge.step.step_number for badge in badges)
            if min_level > 1 and all(badge.step.step_number == min_level for badge in badges):
                user.level = min_level
                user.save()

    @swagger_auto_schema(
        operation_summary="편지 삭제",
        request_body=LetterSerializer,
        responses={
            status.HTTP_204_NO_CONTENT: '삭제 완료',
            status.HTTP_400_BAD_REQUEST: '편지를 찾을 수 없습니다.'
        })
    def delete(self, request):
        user = request.user
        try:
            letter = Letter.objects.filter(Q(sender=user) | Q(receiver=user))
            letter.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Letter.DoesNotExist:
            return Response({"error": "편지를 찾을수없습니다."}, status=status.HTTP_404_NOT_FOUND)


class LetterSendingAPI(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)

    @swagger_auto_schema(
        operation_summary="편지 이미지 전송",
        manual_parameters=[
            openapi.Parameter('file', openapi.IN_FORM, type=openapi.TYPE_FILE, description='저장할 파일')
        ],
    )
    def post(self, request):
        s3_serializer = S3FileUploadSerializer(data=request.data)
        if s3_serializer.is_valid() is False:
            return Response(s3_serializer.errors[0], status=status.HTTP_400_BAD_REQUEST)
        file_url = s3_serializer.save()['file_url']
        match = (Match.objects
                 .filter(requester=request.user, withdraw_reason__isnull=True)
                 .order_by("-created_at")
                 .first()
                 )
        letter = Letter.objects.create(
            sender=request.user,
            receiver=match.acceptor,
            match=match,
            image_url=file_url
        )
        print(f'user: {request.user}')
        request.user.change_letter_status(LetterWritingStatus.BEFORE)
        letter.save()
        letter_serializer = LetterModelSerializer(letter)
        return Response({"letter": letter_serializer.data}, status=status.HTTP_200_OK)
