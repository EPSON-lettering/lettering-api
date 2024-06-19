from django.db.models import Q
from drf_yasg.utils import swagger_auto_schema
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from .models import Letter
from notifications.models import Notification
from .serializers import LetterSerializer


class LetterAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="편지 조회",
    )
    def get(self, request):
        user = request.user
        letters = Letter.objects.filter(Q(sender=user) | Q(receiver=user)).all()
        serializer = LetterSerializer(letters, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_summary="편지 추가",
        request_body=LetterSerializer,
        responses={
            status.HTTP_201_CREATED: LetterSerializer,
            status.HTTP_400_BAD_REQUEST: 'Bad Request'
        }
    )
    def post(self, request):
        serializer = LetterSerializer(data=request.data)
        if serializer.is_valid():
            letter = serializer.save()

            Notification.objects.create(
                user=letter.receiver,
                letter=letter,
                message=f'{request.user.nickname} 님의 편지가 도착했습니다.',
                is_read=False,
                type='received'
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_summary="편지 삭제",
        request_body=LetterSerializer,
        responses={
            status.HTTP_201_CREATED: LetterSerializer,
            status.HTTP_400_BAD_REQUEST: '편지를 찾을수없습니다.'
        })
    def delete(self, request):
        user = request.user
        try:
            letter = Letter.objects.filter(Q(sender=user) | Q(receiver=user))
            letter.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Letter.DoesNotExist:
            return Response({"error": "편지를 찾을수없습니다."}, status=status.HTTP_404_NOT_FOUND)
