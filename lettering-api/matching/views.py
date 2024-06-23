from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
import random
from django.db.models import Q

from interests.models import UserInterest, Interest, Question
from .models import Match, User, MatchRequest
from .serializers import MatchSerializer, MatchRequestSerializer, MatchUserSerializer, SearchMatchDetailsSerializer, \
    IntegrateSearchMatchDetailsSerializer
from .services import CommonInterest
from accounts.serializers import UserSerializer
from accounts.domain import LetterWritingStatus
from interests.serializers import QuestionSerializer


def get_interests(user):
    user_interests = UserInterest.objects.filter(user=user)
    return [user_interest.interest for user_interest in user_interests]


class MatchView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="매칭 찾기",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'nickname': openapi.Schema(type=openapi.TYPE_STRING, description='유저 닉네임'),
            },
            required=['nickname']
        ),
        responses={
            201: openapi.Response('매칭 요청이 생성되었습니다.', MatchRequestSerializer),
            404: openapi.Response('적절한 매칭을 찾을 수 없습니다.'),
            400: openapi.Response('잘못된 요청입니다.'),
            401: openapi.Response('인증되지 않았습니다.')
        }
    )
    def post(self, request):
        nickname = request.data.get('nickname')
        if not nickname:
            return Response({"detail": "닉네임이 필요합니다."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(nickname=nickname)
        except User.DoesNotExist:
            return Response({"detail": "유저를 찾을 수 없습니다."}, status=status.HTTP_404_NOT_FOUND)

        rejected_users = MatchRequest.objects.filter(
            requester=user, state=MatchRequest.REJECTED
        ).values_list('receiver_id', flat=True)

        matched_users = Match.objects.filter(
            state=True,
            withdraw_reason__isnull=True
        ).values_list('requester_id', 'acceptor_id')

        matched_user_ids = set()
        for match_pair in matched_users:
            matched_user_ids.update(match_pair)

        ended_matches = Match.objects.filter(
            Q(requester=user) | Q(acceptor=user),
            state=False,
            withdraw_reason__isnull=False
        ).values_list('requester_id', 'acceptor_id')

        ended_user_ids = set()
        for match_pair in ended_matches:
            ended_user_ids.update(match_pair)

        potential_matches = User.objects.filter(
            language__isnull=False,
            userinterest__interest__in=user.userinterest_set.values_list('interest', flat=True)
        ).exclude(
            Q(id=user.id) | Q(id__in=rejected_users) | Q(id__in=matched_user_ids) | Q(id__in=ended_user_ids)
        ).distinct()

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
            requester_interests = get_interests(user)
            receiver_interests = get_interests(best_match)

            duplicate_interest = CommonInterest(patt=requester_interests, matt=receiver_interests).calculate()
            serializer = MatchRequestSerializer(match_request, interests=duplicate_interest)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response({"detail": "적절한 매칭을 찾을 수 없습니다."}, status=status.HTTP_404_NOT_FOUND)


class MatchRequestView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="매칭 수락 또는 거절",
        manual_parameters=[
            openapi.Parameter('action', openapi.IN_PATH, description="수행할 작업 ('accept' 또는 'reject')",
                              type=openapi.TYPE_STRING)
        ],
        responses={
            200: openapi.Response('매칭 요청이 수락 또는 거절되었습니다.', MatchSerializer),
            404: openapi.Response('매칭 요청을 찾을 수 없습니다.'),
            400: openapi.Response('잘못된 작업입니다.'),
            401: openapi.Response('인증되지 않았습니다.')
        }
    )
    def post(self, request, request_id, action):
        if not request.user.is_authenticated:
            return Response({"detail": "인증 자격 증명이 제공되지 않았습니다."},
                            status=status.HTTP_401_UNAUTHORIZED)

        try:
            match_request = MatchRequest.objects.get(id=request_id)
        except MatchRequest.DoesNotExist:
            return Response({"detail": "매칭 요청을 찾을 수 없습니다."}, status=status.HTTP_404_NOT_FOUND)

        if action == 'accept':
            match_request.state = MatchRequest.ACCEPTED
            match_request.save()

            exists_match = Match.objects.filter(
                Q(requester=match_request.requester, acceptor=match_request.receiver) |
                Q(requester=match_request.receiver, acceptor=match_request.requester),
                state=True,
                withdraw_reason__isnull=True
            ).first()

            if exists_match:
                return Response({"message": "이미 매칭된 사용자입니다."}, status=status.HTTP_400_BAD_REQUEST)

            match = Match.objects.create(
                requester=match_request.requester,
                acceptor=match_request.receiver,
                native_lang=match_request.requester.language,
                learning_lang=match_request.receiver.language,
                state=True
            )
            requester = User.objects.get(id=match_request.requester.id)
            acceptor = User.objects.get(id=match_request.receiver.id)
            requester.change_letter_status(LetterWritingStatus.PROCESSING)
            acceptor.change_letter_status(LetterWritingStatus.PROCESSING)

            serializer = MatchSerializer(match)
            return Response(serializer.data, status=status.HTTP_200_OK)
        elif action == 'reject':
            match_request.state = MatchRequest.REJECTED
            match_request.save()
            return Response({"detail": "매칭 요청이 거절되었습니다."}, status=status.HTTP_200_OK)
        else:
            return Response({"detail": "잘못된 작업입니다."}, status=status.HTTP_400_BAD_REQUEST)


class GetMatchDetailsView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="현재 매칭 정보 조회",
        responses={
            200: openapi.Response('매칭 결과', IntegrateSearchMatchDetailsSerializer()),
        }
    )
    def get(self, req):
        user: User = req.user
        match = (Match.objects
                 .filter(Q(requester=user) | Q(acceptor=user), withdraw_reason__isnull=True, state=True)
                 .order_by("-created_at")
                 .first()
                 )

        if match is None:
            return Response(None, status=200)

        acceptor_id = match.acceptor.id
        acceptor = User.objects.get(id=acceptor_id)
        user_interests = UserInterest.objects.filter(user=acceptor)
        interests = [user_interest.interest for user_interest in user_interests]
        result = IntegrateSearchMatchDetailsSerializer(match, interests=interests)
        print(f'result(serial): {result}')
        return Response(result.data, status=status.HTTP_200_OK)


class GetMatchingListView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="매칭 정보 리스트 조회",
        responses={
            200: openapi.Response('매칭 결과', MatchSerializer(many=True)),
        }
    )
    def get(self, req):
        user: User = req.user
        matches = (Match.objects
                   .filter(Q(requester=user) | Q(acceptor=user), withdraw_reason__isnull=True, state=True)
                   .order_by("-created_at")
                   )
        return Response(MatchSerializer(matches, many=True).data, status=200)


class QuestionView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="현재 질문 조회",
        manual_parameters=[
            openapi.Parameter('match_id', openapi.IN_PATH, description="매칭 ID", type=openapi.TYPE_INTEGER)
        ],
        responses={
            200: openapi.Response(description="현재 질문 조회 성공", schema=QuestionSerializer),
            404: openapi.Response(description="매칭 또는 질문 조회 실패"),
            401: openapi.Response(description="인증되지 않았습니다.")
        }
    )
    def get(self, request, match_id):
        try:
            match = Match.objects.get(
                Q(id=match_id) & (Q(requester=request.user) | Q(acceptor=request.user))
            )
        except Match.DoesNotExist:
            return Response({"detail": "매칭을 찾을 수 없습니다."}, status=status.HTTP_404_NOT_FOUND)

        if not match.current_question:
            return Response({"detail": "현재 질문이 없습니다."}, status=status.HTTP_404_NOT_FOUND)

        serializer = QuestionSerializer(match.current_question)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_summary="질문 제공",
        manual_parameters=[
            openapi.Parameter('match_id', openapi.IN_PATH, description="매칭 ID", type=openapi.TYPE_INTEGER)
        ],
        responses={
            200: openapi.Response(description="질문 제공 성공", schema=QuestionSerializer),
            404: openapi.Response(description="매칭 조회 실패 또는 더 이상 제공할 질문이 없음"),
            401: openapi.Response(description="인증되지 않았습니다.")
        }
    )
    def post(self, request, match_id):
        try:
            match = Match.objects.get(id=match_id, requester=request.user)
        except Match.DoesNotExist:
            return Response({"detail": "매칭을 찾을 수 없습니다."}, status=status.HTTP_404_NOT_FOUND)

        requester_interests = match.requester.userinterest_set.values_list('interest', flat=True)
        acceptor_interests = match.acceptor.userinterest_set.values_list('interest', flat=True)
        common_interests = set(requester_interests) & set(acceptor_interests)

        previous_questions = match.provided_questions.all()
        questions = Question.objects.filter(interest__in=common_interests).exclude(id__in=previous_questions)

        if not questions.exists():
            return Response({"detail": "더 이상 제공할 질문이 없습니다."}, status=status.HTTP_404_NOT_FOUND)

        question = random.choice(questions)
        match.provided_questions.add(question)
        match.current_question = question
        match.save()

        serializer = QuestionSerializer(question)
        return Response(serializer.data, status=status.HTTP_200_OK)


class EndMatchView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="매칭 끊기",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'reason': openapi.Schema(type=openapi.TYPE_STRING, description='매칭 끊는 이유'),
            },
            required=['reason']
        ),
        responses={
            200: openapi.Response(description="매칭 끊기 성공", schema=MatchSerializer),
            404: openapi.Response(description="매칭 조회 실패"),
            401: openapi.Response(description="인증되지 않았습니다.")
        }
    )
    def post(self, request, match_id):
        reason = request.data.get('reason')
        if not reason:
            return Response({"detail": "이유가 필요합니다."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            match = Match.objects.get(id=match_id)
        except Match.DoesNotExist:
            return Response({"detail": "매칭을 찾을 수 없습니다."}, status=status.HTTP_404_NOT_FOUND)

        match.end_match(reason)
        serializer = MatchSerializer(match)
        return Response(serializer.data, status=status.HTTP_200_OK)


class MatchOpponentGetterView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="매칭 상대방 피드 조회",
        responses={
            200: openapi.Response(description="상대방 피드 조회", schema=UserSerializer),
        }
    )
    def get(self, req):
        match = (Match.objects
                 .filter(Q(requester=req.user) | Q(acceptor=req.user), withdraw_reason__isnull=True, state=True)
                 .first()
                 )
        if not match:
            return Response({"message": "매칭이 존재하지 않습니다."}, status=status.HTTP_404_NOT_FOUND)
        opponent = MatchUserSerializer(match.acceptor).data
        user = User.objects.get(id=opponent['id'])
        user_interests = UserInterest.objects.filter(user=user)
        interests = [user_interest.interest for user_interest in user_interests]
        result = UserSerializer(user, interests=interests).data
        return Response(result, status=200)
