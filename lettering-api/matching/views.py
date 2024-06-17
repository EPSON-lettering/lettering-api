from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .models import Match, User, MatchRequest
from .serializers import MatchSerializer, MatchRequestSerializer, MatchUserSerializer, SearchMatchDetailsSerializer


class MatchView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="매칭 찾기",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'nickname': openapi.Schema(type=openapi.TYPE_STRING, description='User nickname'),
            },
            required=['nickname']
        ),
        responses={
            201: openapi.Response('Match request created', MatchRequestSerializer),
            404: openapi.Response('No suitable match found'),
            401: openapi.Response('Unauthorized')
        }
    )
    def post(self, request):
        nickname = request.data.get('nickname')
        if not nickname:
            return Response({"detail": "Nickname is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(nickname=nickname)
        except User.DoesNotExist:
            return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)

        potential_matches = User.objects.filter(
            language__isnull=False,
            userinterest__interest__in=user.userinterest_set.values_list('interest', flat=True)
        ).exclude(id=user.id).distinct()

        best_match = None
        best_match_score = -1

        for potential_user in potential_matches:
            if potential_user.language != user.language:
                common_interests = user.userinterest_set.filter(
                    interest__in=potential_user.userinterest_set.values_list('interest', flat=True)
                ).count()
                if common_interests > best_match_score:
                    best_match = potential_user
                    best_match_score = common_interests

        if best_match:
            match_request = MatchRequest.objects.create(
                requester=user,
                receiver=best_match
            )
            serializer = MatchRequestSerializer(match_request)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response({"detail": "No suitable match found"}, status=status.HTTP_404_NOT_FOUND)


class MatchRequestView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="매칭 수락 또는 거절",
        manual_parameters=[
            openapi.Parameter('action', openapi.IN_PATH, description="Action to perform ('accept' or 'reject')",
                              type=openapi.TYPE_STRING)
        ],
        responses={
            200: openapi.Response('Match request accepted or rejected', MatchSerializer),
            404: openapi.Response('Match request not found'),
            400: openapi.Response('Invalid action'),
            401: openapi.Response('Unauthorized')
        }
    )
    def post(self, request, request_id, action):
        if not request.user.is_authenticated:
            return Response({"detail": "Authentication credentials were not provided."},
                            status=status.HTTP_401_UNAUTHORIZED)

        try:
            match_request = MatchRequest.objects.get(id=request_id, requester=request.user)
        except MatchRequest.DoesNotExist:
            return Response({"detail": "Match request not found"}, status=status.HTTP_404_NOT_FOUND)

        if action == 'accept':
            match_request.state = True
            match_request.save()

            match = Match.objects.create(
                requester=match_request.requester,
                acceptor=match_request.receiver,
                native_lang=match_request.requester.language,
                learning_lang=match_request.receiver.language,
                state=True
            )
            serializer = MatchSerializer(match)
            return Response(serializer.data, status=status.HTTP_200_OK)
        elif action == 'reject':
            match_request.delete()
            return Response({"detail": "Match request rejected"}, status=status.HTTP_200_OK)
        else:
            return Response({"detail": "Invalid action"}, status=status.HTTP_400_BAD_REQUEST)


class GetMatchDetailsView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="현재 매칭 정보 조회",
        responses={
            200: openapi.Response('매칭 결과', SearchMatchDetailsSerializer),
        }
    )
    def get(self, req):
        user: User = req.user
        match = (Match.objects
                 .filter(requester=user, withdraw_reason__isnull=True)
                 .order_by("-created_at")
                 .first()
                 )
        serial = SearchMatchDetailsSerializer(match)
        print(f'match: {serial}')
        if match is None:
            return Response({"matchDetails": None})
        return Response({"matchDetails": serial.data})
