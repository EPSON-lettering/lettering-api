from http import HTTPStatus

import boto3
from botocore.exceptions import ClientError
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.utils import json
from rest_framework.views import APIView
from notifications.models import Notification
from .serializers import EpsonConnectPrintSerializer, EpsonConnectAuthSerializer, EpsonScanSerializer, \
    EpsonConnectEmailSerializer
from urllib import request, parse, error
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
        operation_summary="Epson 프린터에 파일 출력하기",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'file': openapi.Schema(type=openapi.TYPE_FILE, description='출력할 파일'),
                'letter_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='편지 ID'),
            },
            required=['deviceEmail', 'file', 'letter_id']
        ),
        responses={
            status.HTTP_200_OK: openapi.Response('프린트 성공'),
            status.HTTP_400_BAD_REQUEST: openapi.Response('프린트 실패'),
            status.HTTP_404_NOT_FOUND: openapi.Response('편지 찾을 수 없음'),
            status.HTTP_405_METHOD_NOT_ALLOWED: openapi.Response('API호출 불가, 아직 파일이 업로드되기 전')
        }
    )
    def post(self, request_data):

        device = request_data.data['deviceEmail']
        file = request_data.FILES.get('file')
        letter_id = request_data.data.get('letter_id')
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

        try:
            letter = Letter.objects.get(id=letter_id)
        except Letter.DoesNotExist:
            return Response({'error': 'Letter not found'}, status=status.HTTP_404_NOT_FOUND)

        Notification.objects.create(
            letter=letter,
            message=f'{user.nickname} 님이 편지를 작성 중입니다.',
            is_read=False
        )
        return Response({'message': "프린트가 성공적으로 완료되었습니다"}, status=status.HTTP_200_OK)


class ScannerDestinationsView(APIView):
    permission_classes = []

    @swagger_auto_schema(
        operation_summary="앱손 프린터 스캔",
        request_body=EpsonConnectPrintSerializer,
        responses={200: "available: boolean, error: string"}
    )
    def post(self, request_data):
        host = HOST
        accept = ACCEPT
        auth_uri = EPSON_URL
        client_id = CLIENT_ID
        secret = SECRET
        device = request_data.data['deviceEmail']
        auth = base64.b64encode(f'{client_id}:{secret}'.encode()).decode()

        data = {
            'grant_type': 'password',
            'username': device,
            'password': ''
        }

        headers = {
            'Host': host,
            'Accept': accept,
            'Authorization': f'Basic {auth}',
            'Content-Type': 'application/x-www-form-urlencoded; charset=utf-8'
        }
        try:
            response = requests.post(auth_uri, data=data, headers=headers)
            response.raise_for_status()
            auth_result = response.json()
        except requests.exceptions.RequestException as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        subject_id = auth_result['subject_id']
        access_token = auth_result['access_token']
        add_uri = f'https://{host}/api/1/scanning/scanners/{subject_id}/destinations'

        if requests.get(add_uri).status_code != 200:
            data_param = {
                'alias_name': 'send',
                'type': 'url',
                'destination': os.environ.get('EPSON_SCAN_DIRECTION'),
            }
            data = json.dumps(data_param)

            headers = {
                'Host': host,
                'Accept': accept,
                'Authorization': f'Bearer {access_token}',
                'Content-Length': str(len(data)),
                'Content-Type': 'application/json;charset=utf-8'
            }

            try:
                response = requests.post(add_uri, data=data, headers=headers, verify=False)
                response.raise_for_status()
                add_result = {
                    'Response': {
                        'Header': dict(response.headers),
                        'Body': response.json()
                    }
                }
                return Response({"success":"스캔 대상 추가에 성공했습니다!"}, status=status.HTTP_200_OK)
            except requests.exceptions.RequestException as e:
                return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class FileUploadView(APIView):
    def post(self, request):
        serializer = EpsonScanSerializer(data=request.data)
        if serializer.is_valid():
            # 파일 업로드
            for file in request.FILES.values():
                self.upload_to_s3(file)
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def upload_to_s3(self, file):
        s3 = boto3.client(
            's3',
            aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY'),
        )
        try:
            s3.upload_fileobj(
                file,
                os.environ.get('AWS_BUCKET_NAME'),
                file.user
            )
        except ClientError as e:
            print(f"Error uploading file to S3: {e}")
            return False
        return True


class EpsonConnectEmailAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="앱손 이메일 연결 확인",
        request_body=EpsonConnectEmailSerializer,
        responses={200: "available: boolean, error: string"}
    )
    def post(self, request_data):
        device = request_data.data['epsonEmail']
        user = request_data.user
        # 인증
        auth_uri = EPSON_URL
        auth = base64.b64encode((CLIENT_ID + ':' + SECRET).encode()).decode()
        context = {"verify": False}

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
        serializer = EpsonConnectEmailSerializer(data=request_data.data, context={'request': request, 'user': user})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"success":"생성이 완료되었습니다"}, status=status.HTTP_201_CREATED)
