from drf_yasg.utils import swagger_auto_schema
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import NicknameCheckSerializer


class NicknameCheckView(APIView):

    @swagger_auto_schema(operation_summary="nickName 중복 확인",request_body=NicknameCheckSerializer)
    def post(self, request):
        serializer = NicknameCheckSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        is_unique = serializer.validated_data['nickname']
        return Response({"isUnique": is_unique})
