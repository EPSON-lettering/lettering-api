import base64
import json
from urllib import parse, error
from urllib import request as urllib_request
from ssl import SSLCertVerificationError
import ssl
import os
import certifi


EPSON_URL = os.environ.get('EPSON_URL')
CLIENT_ID = os.environ.get('EPSON_CLIENT_ID')
SECRET = os.environ.get('EPSON_SECRET')
HOST = os.environ.get('EPSON_HOST')
ACCEPT = os.environ.get('EPSON_ACCEPT')
auth_uri = EPSON_URL
auth = base64.b64encode(f'{CLIENT_ID}:{SECRET}'.encode()).decode()


def get_auth_headers(device_email: str):
    query_param = {
        'grant_type': 'password',
        'username': device_email,
        'password': ''
    }
    query_string = parse.urlencode(query_param)

    req = urllib_request.Request(auth_uri, data=query_string.encode('utf-8'), headers=headers, method='POST')
    context = ssl.create_default_context(cafile=certifi.where())
    with urllib_request.urlopen(req, context=context) as res:
        body = res.read()
    auth_data = json.loads(body)
    access_token = auth_data.get('access_token')

    auth_headers = {
        'Authorization': 'Basic ' + auth,
        'Content-Type': 'application/x-www-form-urlencoded; charset=utf-8'
    }

    work_headers = {
        'Authorization': 'Bearer ' + access_token,
        'Content-Type': 'application/json;charset=utf-8'
    }

    return [auth_headers, work_headers, query_string]
