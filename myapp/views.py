from django.shortcuts import render
from django.shortcuts import render
from rest_framework.decorators import APIView
from rest_framework import  status
from rest_framework.response import Response

from intuitlib.client import AuthClient
from intuitlib.enums import Scopes
from django.conf import settings
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseServerError
from django.shortcuts import render, redirect
from .services import qbo_api_call
from .models import *
from .serializers import *
import json

# Create your views here.

class Oauth(APIView):
    def get(self, request):
        auth_client = AuthClient(
            settings.CLIENT_ID, 
            settings.CLIENT_SECRET, 
            settings.REDIRECT_URI, 
            settings.ENVIRONMENT,
        )
        url = auth_client.get_authorization_url([Scopes.ACCOUNTING])
        request.session['state'] = auth_client.state_token
        return Response(url)


def callback(request):
    auth_client = AuthClient(
        settings.CLIENT_ID, 
        settings.CLIENT_SECRET, 
        settings.REDIRECT_URI, 
        settings.ENVIRONMENT, 
        state_token=request.session.get('state', None),
    )

    state_tok = request.GET.get('state', None)
    error = request.GET.get('error', None)
    
    if error == 'access_denied':
        return HttpResponse('access_denied')
    
    if state_tok is None:
        return HttpResponseBadRequest()
    elif state_tok != auth_client.state_token:  
        return HttpResponse('unauthorized', status=401)
    
    auth_code = request.GET.get('code', None)
    realm_id = request.GET.get('realmId', None)
    request.session['realm_id'] = realm_id

    if auth_code is None:
        return HttpResponseBadRequest()

    try:
        auth_client.get_bearer_token(auth_code, realm_id=realm_id)
        request.session['access_token'] = auth_client.access_token
        request.session['refresh_token'] = auth_client.refresh_token
        request.session['id_token'] = auth_client.id_token
        QBODetails.objects.all().delete()
        QBODetails.objects.create(
            auth_code = auth_code,
            realm_id = realm_id,
            access_token = auth_client.access_token,
            refresh_token = auth_client.refresh_token,
            id_token = auth_client.id_token
        )
    except AuthClientError as e:
        # just printing status_code here but it can be used for retry workflows, etc
        print(e.status_code)
        print(e.content)
        print(e.intuit_tid)
    except Exception as e:
        print(e)
    # breakpoint()

    return HttpResponse('connected')

class QBOGet(APIView):
    def get(self, request):
        request_type = request.GET.get('request_type', None)
        if isinstance(request_type, type(None)):
            content = {
                "error" : "Please provide the request type"
            }
            return Response(content, status=status.HTTP_400_BAD_REQUEST)
        else:
            try:
                request_method = "GET"
                response = qbo_api_call(request_method, request_type)
                content = {
                    "response" : json.loads(response.content),
                    "status" : response.status_code
                }
            except:
                content = {
                    "response" : "Invalid request type",
                    "status" : 401
                }
            return Response(content, status=status.HTTP_200_OK)


class QBOPost(APIView):
    def get(self, request):
        content = {
                    "message" : "Please provide the request type and it's payload",
                }
        return Response(content, status=status.HTTP_200_OK)
    def post(self, request):
        data = request.data
        try:
            request_type = data['request_type']
        except:
            content = {
                "error" : "Please provide the request type"
            }
            return Response(content, status=status.HTTP_400_BAD_REQUEST)
        try:
            payload = data['payload']
        except:
            content = {
                "error" : "Please provide the payload"
            }
            return Response(content, status=status.HTTP_400_BAD_REQUEST)
        try:
            request_method = "POST"
            payload = json.dumps(payload)
            response = qbo_api_call(request_method, request_type, payload)
            content = {
                "response" : json.loads(response.content),
                "status" : response.status_code
            }
        except:
            content = {
                "response" : "Invalid request type",
                "status" : 401
            }
        return Response(content, status=status.HTTP_200_OK)

class TempView(APIView):
    def get(self, request):
        if settings.DEBUG:
            qbo_details = QBODetails.objects.first()
            serilized = QBODetailsSerializer(qbo_details).data
            return Response(serilized, status = status.HTTP_200_OK)
        else:
            content = {
                "error" : "This view is only available in debug"
            }
            return Response(content, status = status.HTTP_403_FORBIDDEN)
