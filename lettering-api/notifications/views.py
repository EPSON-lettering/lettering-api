from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from .models import Notification
from .serializers import NotificationSerializer

class NotificationAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="알림 조회",
        responses={200: NotificationSerializer(many=True)}
    )
    def get(self, request):
        user = request.user
        notifications = Notification.objects.filter(letter__receiver=user).all()
        serializer = NotificationSerializer(notifications, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_summary="알림 읽음 처리",
        responses={200: "Success", 404: "Not Found"}
    )
    def put(self, request, notification_id):
        try:
            notification = Notification.objects.get(id=notification_id, letter__receiver=request.user)
        except Notification.DoesNotExist:
            return Response({"detail": "Not Found"}, status=status.HTTP_404_NOT_FOUND)

        notification.is_read = True
        notification.save()
        return Response({"message": "Notification marked as read"}, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_summary="알림 삭제",
        responses={204: "No Content", 404: "Not Found"}
    )
    def delete(self, request, notification_id):
        try:
            notification = Notification.objects.get(id=notification_id, letter__receiver=request.user)
        except Notification.DoesNotExist:
            return Response({"detail": "Not Found"}, status=status.HTTP_404_NOT_FOUND)

        notification.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
