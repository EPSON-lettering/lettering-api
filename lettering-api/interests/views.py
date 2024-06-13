from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Interest, UserInterest
from .serializers import InterestSerializer, UserInterestSerializer


class InterestView(APIView):
    def get(self, request):
        queryset = Interest.objects.all()
        serializer = InterestSerializer(queryset, many=True)
        return Response(serializer.data)


class UserInterestView(APIView):
    @swagger_auto_schema(operation_summary="nickname 중복 확인", request_body=UserInterestSerializer)
    def post(self, request):
        try:
            data = request.data['data']
            for interest in data:
                serializer = InterestSerializer(data=interest)
                if serializer.is_valid():
                    interest = serializer.save()

                    UserInterest.objects.create(
                        user=request.user,
                        interest=interest,
                    )
            return Response("성공했습니다 ", status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
