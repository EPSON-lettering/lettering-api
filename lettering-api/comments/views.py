from django.db.models import Q
from drf_yasg.utils import swagger_auto_schema
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from .models import Comment, Reply
from letters.models import Letter
from notifications.models import Notification
from .serializers import CommentSerializer, ReplySerializer
from badges.models import Badge, UserBadge

class CommentAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="댓글/피드백 조회",
    )
    def get(self, request, letter_id):
        user = request.user
        comments = Comment.objects.filter(letter_id=letter_id).all()
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
        data = request.data
        data['letter'] = letter_id
        serializer = CommentSerializer(data=data, context={'request': request})
        if serializer.is_valid():
            comment = serializer.save()
            if comment.type == 'feedback':
                self.award_badge(comment.sender, '피드백 마스터')

            elif comment.type == 'chat':
                self.award_badge(comment.sender, '답장의 제왕')
            self.update_user_level(comment.sender)
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
        user = request.user
        replies = Reply.objects.filter(comment_id=comment_id).all()
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
        data = request.data
        data['comment'] = comment_id
        serializer = ReplySerializer(data=data, context={'request': request})
        if serializer.is_valid():
            reply = serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
