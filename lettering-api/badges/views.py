from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_yasg.utils import swagger_auto_schema

from accounts.models import User
from matching.models import Match
from .serializers import UserBadgeSerializer, BadgeSerializer
from .models import UserBadge, Badge


class BadgeAPIView(APIView):
    @swagger_auto_schema(
        operation_summary="전체 뱃지 조회",
        responses={200: BadgeSerializer(many=True)}
    )
    def get(self, request):
        badges = Badge.objects.all()
        serializer = BadgeSerializer(badges, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class PartnerBadgeAPIView(APIView):
    @swagger_auto_schema(
        operation_summary="대화 상대 뱃지 조회"
    )
    def get(self, request):
        print(request.user)
        user = request.user
        match = (Match.objects
                 .filter(acceptor=user, withdraw_reason__isnull=True)
                 .order_by("-created_at")
                 .first()
                 )
        partner = match.requester
        if match is None:
            match = (Match.objects
                     .filter(requester=user, withdraw_reason__isnull=True)
                     .order_by("-created_at")
                     .first()
                     )
            partner = match.acceptor
        user_badges = UserBadge.objects.filter(user=partner)
        serializer = UserBadgeSerializer(user_badges, many=True)
        print(serializer.data)
        return Response(serializer.data, status=status.HTTP_200_OK)


class UserBadgeAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="사용자 뱃지 조회",
        responses={200: UserBadgeSerializer(many=True)}
    )
    def get(self, request):
        user_badges = UserBadge.objects.filter(user=request.user)
        serializer = UserBadgeSerializer(user_badges, many=True)
        print(serializer.data)
        return Response(serializer.data, status=status.HTTP_200_OK)