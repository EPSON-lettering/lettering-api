from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Interest, UserInterest
from .serializers import InterestSerializer, UserInterestChangeSerializer
from rest_framework.permissions import IsAuthenticated, AllowAny


class InterestView(APIView):
    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        elif self.request.method == 'POST':
            return [IsAuthenticated()]
        return super().get_permissions()

    @swagger_auto_schema(
        operation_summary="관심사 List",
        responses={200: InterestSerializer(many=True)}
    )
    def get(self, request):
        queryset = Interest.objects.all()
        serializer = InterestSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_summary="관심사 변경",
        request_body=UserInterestChangeSerializer,
        responses={200: "성공", 400: "잘못된 요청"}
    )
    def post(self, request):
        serializer = UserInterestChangeSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response(status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)