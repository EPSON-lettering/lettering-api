from http import HTTPStatus

from drf_yasg.utils import swagger_auto_schema
from rest_framework import status, serializers
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.utils import json
from rest_framework.views import APIView
from .serializers import EpsonConnectPrintSerializer, EpsonConnectAuthSerializer
from urllib import request, parse, error
from .models import EpsonConnectEmail
from drf_yasg import openapi
import base64
import requests
import os

EPSON_URL = os.environ.get('EPSON_URL')
CLIENT_ID = os.environ.get('EPSON_CLIENT_ID')
SECRET = os.environ.get('EPSON_SECRET')
HOST = os.environ.get('EPSON_HOST')
ACCEPT = os.environ.get('EPSON_ACCEPT')


class EpsonPrintConnectAPI(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        request_body=EpsonConnectPrintSerializer,
    )
    def post(self, request_data):

        device = request_data.data['deviceEmail']
        file = request_data.FILES
        # 1. Authentication
        auth_uri = EPSON_URL
        auth = base64.b64encode((CLIENT_ID + ':' + SECRET).encode()).decode()


        query_param = {
            'grant_type': 'password',
            'username': device,
            'password': ''
        }
        query_string = parse.urlencode(query_param)

        headers = {
            'Authorization': 'Basic ' + auth,
            'Content-Type': 'application/x-www-form-urlencoded; charset=utf-8'
        }

        try:
            req = request.Request(auth_uri, data=query_string.encode('utf-8'), headers=headers, method='POST')
            with request.urlopen(req) as res:
                body = res.read()
        except error.HTTPError as err:
            return Response({'error': f'{err.code}:{err.reason}:{str(err.read())}'}, status=status.HTTP_400_BAD_REQUEST)
        except error.URLError as err:
            return Response({'error': err.reason}, status=status.HTTP_400_BAD_REQUEST)

        if res.status != HTTPStatus.OK:
            return Response({'error': f'{res.status}:{res.reason}'}, status=status.HTTP_400_BAD_REQUEST)
        auth_data = json.loads(body)
        subject_id = auth_data.get('subject_id')
        access_token = auth_data.get('access_token')
# 프린트에게 전달할 id 및 Url 생성

        job_uri = f'https://{HOST}/api/1/printing/printers/{subject_id}/jobs'

        data_param = {
            'job_name': 'Print',
            'print_mode': 'photo'
        }
        data = json.dumps(data_param)

        headers = {
            'Authorization': 'Bearer ' + access_token,
            'Content-Type': 'application/json;charset=utf-8'
        }

        try:
            req = request.Request(job_uri, data=data.encode('utf-8'), headers=headers, method='POST')
            with request.urlopen(req) as res:
                body = res.read()
        except error.HTTPError as err:
            return Response({'error': f'{err.code}:{err.reason}:{str(err.read())}'}, status=status.HTTP_400_BAD_REQUEST)
        except error.URLError as err:
            return Response({'error': err.reason}, status=status.HTTP_400_BAD_REQUEST)

        if res.status != HTTPStatus.CREATED:
            return Response({'error': f'{res.status}:{res.reason}'}, status=status.HTTP_400_BAD_REQUEST)
        job_data = json.loads(body)

        job_id = job_data.get('id')
        base_uri = job_data.get('upload_uri')

        # 프린트 파일  업로드
        local_file_path = file.name
        _, ext = os.path.splitext(local_file_path)
        file_name = '1' + ext
        upload_uri = base_uri + '&File=' + file_name

        headers = {
            'Content-Length': str(os.path.getsize(local_file_path)),
            'Content-Type': 'application/octet-stream'
        }

        try:
            with open(local_file_path, 'rb') as f:
                req = request.Request(upload_uri, data=f, headers=headers, method='POST')
                with request.urlopen(req) as res:
                    body = res.read()
        except error.HTTPError as err:
            return Response({'error': f'{err.code}:{err.reason}:{str(err.read())}'}, status=status.HTTP_400_BAD_REQUEST)
        except error.URLError as err:
            return Response({'error': err.reason}, status=status.HTTP_400_BAD_REQUEST)

        if res.status != HTTPStatus.OK:
            return Response({'error': f'{res.status}:{res.reason}'}, status=status.HTTP_400_BAD_REQUEST)
# 파일 출력

        print_uri = f'https://{HOST}/api/1/printing/printers/{subject_id}/jobs/{job_id}/print'
        data = ''

        headers = {
            'Authorization': 'Bearer ' + access_token,
            'Content-Type': 'application/json; charset=utf-8'
        }

        try:
            req = request.Request(print_uri, data=data.encode('utf-8'), headers=headers, method='POST')
            with request.urlopen(req) as res:
                body = res.read()
        except error.HTTPError as err:
            return Response({'error': f'{err.code}:{err.reason}:{str(err.read())}'}, status=status.HTTP_400_BAD_REQUEST)
        except error.URLError as err:
            return Response({'error': err.reason}, status=status.HTTP_400_BAD_REQUEST)

        if res.status != HTTPStatus.OK:
            return Response({'error': f'{res.status}:{res.reason}'}, status=status.HTTP_400_BAD_REQUEST)

        return Response({'message': "프린트가 성공적으로 완료되었습니다"}, status=status.HTTP_200_OK)


class EpsonConnectAuthView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="앱손 프린터",
        responses={200: "available: boolean, error: string"}
    )
    def get(self, request):
        auths = EpsonConnectEmail.objects.filter(user=request.user)
        serializer = EpsonConnectAuthSerializer(auths, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, requset):
        userEmail = EpsonConnectEmail.objects.filter(user=request.user)
        if not userEmail:
            return Response("이메일을 등록 하셔야합니다!")


class UserEpsonConnectView(APIView):
    def post(self, request):
        email = request.data.get('email')
        if email:
            user = request.user  # 현재 로그인한 사용자
            try:
                obj, created = EpsonConnectEmail.objects.get_or_create(
                    user=user, deviceEmail=email
                )
                if created:
                    serializer = EpsonConnectAuthSerializer(obj)
                    return Response(serializer.data, status=status.HTTP_201_CREATED)
                else:
                    return Response({'error': 'Email already exists'}, status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'error': '이메일이 필요합니다'}, status=status.HTTP_400_BAD_REQUEST)
