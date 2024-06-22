from http import HTTPStatus
from ssl import SSLCertVerificationError

import boto3
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.parsers import JSONParser, FormParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.utils import json
from rest_framework.views import APIView
from notifications.models import Notification
from .serializers import EpsonConnectPrintSerializer, EpsonScanSerializer, EpsonConnectEmailSerializer
from urllib import parse, error
from urllib import request as urllib_request
import base64, requests, os
from PIL import Image
from letters.models import Letter
from accounts.models import User
from accounts.domain import LetterWritingStatus
from .models import EpsonConnectScanData
import ssl
import certifi


EPSON_URL = os.environ.get('EPSON_URL')
CLIENT_ID = os.environ.get('EPSON_CLIENT_ID')
SECRET = os.environ.get('EPSON_SECRET')
HOST = os.environ.get('EPSON_HOST')
ACCEPT = os.environ.get('EPSON_ACCEPT')


class EpsonLetterIdPrintConnectAPI(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)

    @swagger_auto_schema(
        operation_summary="Epson 프린터에 파일 출력하기",
        manual_parameters=[
            openapi.Parameter('letter_id', openapi.IN_FORM, type=openapi.TYPE_INTEGER, description='편지 ID'),
        ],
        responses={
            status.HTTP_200_OK: openapi.Response('프린트 성공'),
            status.HTTP_400_BAD_REQUEST: openapi.Response('프린트 실패'),
            status.HTTP_404_NOT_FOUND: openapi.Response('편지 찾을 수 없음'),
            status.HTTP_405_METHOD_NOT_ALLOWED: openapi.Response('API호출 불가, 아직 파일이 업로드되기 전')
        }
    )
    def post(self, request_data, letter_id):
        letter = Letter.objects.get(id=letter_id)
        device = letter.receiver.epson_email
        image_url = letter.image_url
        s3 = boto3.resource('s3')
        bucket = s3.Bucket(os.environ.get('AWS_STORAGE_BUCKET_NAME'))
        obj = bucket.Object(image_url)
        response = obj.get()
        file_stream = response['Body']
        file = Image.open(file_stream)

        # 1. Authentication
        auth_uri = EPSON_URL
        auth = auth = base64.b64encode(f'{CLIENT_ID}:{SECRET}'.encode()).decode()

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
            user=letter.receiver,
            letter=letter,
            message=f'{request.user.nickname} 님이 편지를 작성 중입니다!',
            is_read=False,
            type='print_started'
        )



        user = request.user
        user.status_message = LetterWritingStatus.PROCESSING
        user.save()

        return Response({'message': "프린트가 성공적으로 완료되었습니다"}, status=status.HTTP_200_OK)


class ChangeUserWritingSatusAPI(APIView):

    @swagger_auto_schema(
        operation_summary="사용자 편지 작성 중 상태 변경 API",
        responses={
            status.HTTP_200_OK: openapi.Response('편지 작성 중 상태로 변경'),
        }
    )
    def patch(self, request):
        user = User.objects.get(id=request.user.id)
        user.change_letter_status(LetterWritingStatus.PROCESSING)
        return Response({"message": None}, status=200)


class EpsonPrintConnectAPI(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [JSONParser, FormParser, MultiPartParser]
    parser_classes = (MultiPartParser, FormParser)

    @swagger_auto_schema(
        operation_summary="Epson 프린터에 올린 파일 출력하기",
        manual_parameters=[
            openapi.Parameter('file', openapi.IN_FORM, type=openapi.TYPE_FILE, description='출력할 파일')
        ],
        responses={
            status.HTTP_200_OK: openapi.Response('프린트 성공'),
            status.HTTP_400_BAD_REQUEST: openapi.Response('프린트 실패'),
            status.HTTP_404_NOT_FOUND: openapi.Response('편지 찾을 수 없음'),
            status.HTTP_405_METHOD_NOT_ALLOWED: openapi.Response('API호출 불가, 아직 파일이 업로드되기 전')
        }
    )
    def post(self, request_data):
        file = request_data.FILES.get('file')
        device = request_data.user.epson_email
        # 1. Authentication
        auth_uri = EPSON_URL
        auth = base64.b64encode(f'{CLIENT_ID}:{SECRET}'.encode()).decode()

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
        _, ext = os.path.splitext(file.name)
        file_name = '1' + ext
        upload_uri = base_uri + '&File=' + file_name

        headers = {
            'Content-Length': str(file.size),
            'Content-Type': 'application/octet-stream'
        }

        try:
            req = request.Request(upload_uri, data=file, headers=headers, method='POST')
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
        return Response({'message : 프린트가 성공적으로 완료되었습니다'}, status=status.HTTP_200_OK)


class ScannerDestinationsView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="앱손 프린터 스캔 대상 추가",
        responses={200: "available: boolean, error: string"}
    )
    def post(self, request_data):
        host = HOST
        accept = ACCEPT
        auth_uri = EPSON_URL
        client_id = CLIENT_ID
        secret = SECRET
        device = request_data.user.epson_email
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
                'alias_name': 'lettering',
                'type': 'url',
                'destination': f'{os.environ.get("EPSON_SCAN_DIRECTION")}/{request_data.user.username}',
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
                return Response({"success:스캔 대상 추가에 성공했습니다!"}, status=status.HTTP_200_OK)
            except requests.exceptions.RequestException as e:
                return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class FileUploadView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [JSONParser, FormParser, MultiPartParser]
    parser_classes = (MultiPartParser, FormParser)
    @swagger_auto_schema(
        operation_summary="유저가 스캐너가 없을 때 사진 업로드 후 저장",
        manual_parameters=[
            openapi.Parameter('imagefile', openapi.IN_FORM, type=openapi.TYPE_FILE, description='저장할 파일')
        ],
        responses={
            status.HTTP_201_CREATED: openapi.Response('message: 전송이 완료되었습니다'),
            status.HTTP_400_BAD_REQUEST: openapi.Response('매칭 정보를 찾을 수 없습니다'),
            status.HTTP_400_BAD_REQUEST: openapi.Response('편지 저장에 실패했습니다.'),
        }
    )
    def post(self, request ):
        serializer = EpsonScanSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "다운로드가 완료되었습니다."}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ToEpsonFileUploadView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [JSONParser, FormParser, MultiPartParser]
    parser_classes = (MultiPartParser, FormParser)
    @swagger_auto_schema(
        operation_summary="Epson 프린터 스캔 후 저장",
        responses={
            status.HTTP_201_CREATED: openapi.Response('message: 전송이 완료되었습니다'),
            status.HTTP_400_BAD_REQUEST: openapi.Response('매칭 정보를 찾을 수 없습니다'),
            status.HTTP_400_BAD_REQUEST: openapi.Response('편지 저장에 실패했습니다.'),
        }
    )
    def post(self, request , username):
        serializer = EpsonScanSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response({"message: 전송이 완료되었습니다"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class EpsonConnectEmailAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="앱손 이메일 연결 확인",
        request_body=EpsonConnectEmailSerializer,
        responses={
            status.HTTP_200_OK: 'message : 연결이 완료 되었습니다!',
            status.HTTP_400_BAD_REQUEST: 'error : 잘못된 요청입니다!',
        }
    )
    def post(self, request):
        device = request.data['epsonEmail']
        serializer = EpsonConnectEmailSerializer(data=request.data, context={'request': request})

        # 인증
        auth_uri = EPSON_URL
        auth = base64.b64encode(f'{CLIENT_ID}:{SECRET}'.encode()).decode()

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
            req = urllib_request.Request(auth_uri, data=query_string.encode('utf-8'), headers=headers, method='POST')
            context = ssl.create_default_context(cafile=certifi.where())
            with urllib_request.urlopen(req, context=context) as res:
                body = res.read()
                res_status = res.status
        except error.HTTPError as err:
            return Response({'error': f'{err.code}:{err.reason}:{str(err.read())}'}, status=status.HTTP_400_BAD_REQUEST)
        except error.URLError as err:
            return Response({'error': err.reason}, status=status.HTTP_400_BAD_REQUEST)
        except ssl.SSLError as err:
            return Response({'error': str(err)}, status=status.HTTP_400_BAD_REQUEST)

        if res_status != HTTPStatus.OK:
            return Response({'error': f'{res_status}:{res.reason}'}, status=status.HTTP_400_BAD_REQUEST)

        if serializer.is_valid():
            serializer.save()
            return Response({"message": "연결이 완료 되었습니다!"}, status=status.HTTP_201_CREATED)
        return Response({"error": "잘못된 요청입니다!"}, status=status.HTTP_400_BAD_REQUEST)


class ScanDataAPIView(APIView):
    @swagger_auto_schema(
        operation_summary="최근에 스캔한 혹은 가져온 이미지 URL 가져오기",
        responses={
            status.HTTP_200_OK : "imageUrl",
        }
    )
    def get(self, request_data):
        ScanData = EpsonConnectScanData.objects.filter(user=request_data.user).order_by('-id')[0]
        imageUrl = ScanData.imageUrl
        rid = ScanData.id
        return Response({'success' : {"imageUrl": str(imageUrl), "id": str(id)}})



