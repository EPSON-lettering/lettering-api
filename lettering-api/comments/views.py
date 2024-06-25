from django.db.models import Q
from drf_yasg.utils import swagger_auto_schema
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from accounts.models import User
from .models import Comment, Reply
from letters.models import Letter
from notifications.models import Notification
from .serializers import CommentSerializer, ReplySerializer
from badges.models import Badge, UserBadge
from .services import get_receiver


class CommentAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="댓글/피드백 조회",
    )
    def get(self, request, letter_id):
        comments = Comment.objects.filter(letter_id=letter_id).all().order_by("created_at")
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_summary="댓글/피드백 추가",
        request_body=CommentSerializer,
        responses={
            status.HTTP_201_CREATED: CommentSerializer,
            status.HTTP_400_BAD_REQUEST: 'Bad Request'
        }
    )
    def post(self, request, letter_id):
        body = request.data
        sender: User = request.user
        letter: Letter = Letter.objects.get(id=letter_id)
        receiver = get_receiver([letter.sender, letter.receiver], sender)
        type = body['type']
        message = body.get("message")
        image = body.get("image")

        comment = Comment.objects.create(
            type=type,
            letter=letter,
            sender=sender,
            receiver=receiver,
            message=message,
            image=image,
        )

        # 알림 생성
        Notification.objects.create(
            user=receiver,
            comment=comment,
            message=f'{sender.nickname} 님이 새로운 {type}을(를) 보냈습니다!',
            type='comment'
        )

        if type == 'feedback':
            self.award_badge(sender, '피드백 마스터')
        if type == 'chat':
            self.award_badge(sender, '답장의 제왕')
        self.update_user_level(sender)

        serialized_comment = CommentSerializer(comment, sender_data=sender)
        return Response(serialized_comment.data, status=201)

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
                user_badge.progress = user_badge.step.required_count
        user_badge.save()

    def update_user_level(self, user):
        badges = UserBadge.objects.filter(user=user)
        if badges.exists():
            min_level = min(badge.step.step_number for badge in badges)
            if min_level > 1 and all(badge.step.step_number == min_level for badge in badges):
                user.level = min_level
                user.save()


class ReplyAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="답글 조회",
    )
    def get(self, request, comment_id):
        replies = Reply.objects.filter(comment_id=comment_id).all().order_by("created_at")
        serializer = ReplySerializer(replies, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_summary="답글 추가",
        request_body=ReplySerializer,
        responses={
            status.HTTP_201_CREATED: ReplySerializer,
            status.HTTP_400_BAD_REQUEST: 'Bad Request'
        }
    )
    def post(self, request, comment_id):
        body = request.data
        comment = Comment.objects.get(id=comment_id)
        receiver = get_receiver([comment.receiver, comment.sender], request.user)
        reply = Reply.objects.create(
            comment=comment,
            sender=request.user,
            receiver=receiver,
            message=body["message"],
            image=body.get("image", None)
        )

        Notification.objects.create(
            user=receiver,
            reply=reply,
            message='내 피드백/채팅에 새로운 답글이 달렸습니다!',
            type='reply'
        )

        return Response(ReplySerializer(reply).data, status=status.HTTP_201_CREATED)