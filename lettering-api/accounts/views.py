from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import NicknameCheckSerializer


class NicknameCheckView(APIView):
    def post(self, request):
        serializer = NicknameCheckSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        is_unique = serializer.validated_data['nickname']
        return Response({"isUnique": is_unique})
