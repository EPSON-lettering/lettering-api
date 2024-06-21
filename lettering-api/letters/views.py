from django.db.models import Q
from drf_yasg.utils import swagger_auto_schema
from rest_framework.parsers import JSONParser, FormParser, MultiPartParser
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from .models import Letter
from notifications.models import Notification
from .serializers import LetterSerializer


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
    def post(self, request, scanDataId):
        serializer = LetterSerializer(data=request.data, context={'request': request, 'scanDataId': scanDataId})
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
            letter.sender.status_message = '편지를 전송하였습니다!'
            letter.sender.save()
            letter.receiver.status_message = '편지를 수령하였습니다!'
            letter.receiver.save()

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def award_badge(self, user, badge_name):
        badge = Badge.objects.get(name=badge_name)
        current_step = badge.steps.order_by('step_number').first()

        user_badge, created = UserBadge.objects.get_or_create(
            user=user,
            badge=badge,
            defaults={'step': current_step, 'progress': 0}
        )

        user_badge.progress += 1
        if user_badge.progress >= user_badge.step.required_count:
            next_step = badge.steps.filter(step_number=user_badge.step.step_number + 1).first()
            if next_step:
                user_badge.step = next_step
                user_badge.progress = 0
            else:
                user_badge.progress = user_badge.step.required_count  # 최종 단계에서는 더 이상 진행하지 않음
        user_badge.save()

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
