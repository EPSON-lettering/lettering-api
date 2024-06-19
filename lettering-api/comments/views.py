from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from .models import Comment, Reply
from .serializers import CommentSerializer, ReplySerializer
from drf_yasg.utils import swagger_auto_schema

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
            serializer.save(sender=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

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
            serializer.save(sender=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
