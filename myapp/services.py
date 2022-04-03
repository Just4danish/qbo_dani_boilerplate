import requests
from django.conf import settings
from .models import QBODetails
from intuitlib.client import AuthClient
import json

def qbo_api_call(request_method, request_type, payload=None):
    qbo_details = QBODetails.objects.first()
    auth_code = qbo_details.auth_code
    realm_id = qbo_details.realm_id
    access_token = qbo_details.access_token
    refresh_token = qbo_details.refresh_token
    id_token = qbo_details.id_token
    auth_client = AuthClient(
        settings.CLIENT_ID, 
        settings.CLIENT_SECRET, 
        settings.REDIRECT_URI, 
        settings.ENVIRONMENT, 
        access_token=access_token, 
        refresh_token=refresh_token, 
        realm_id=realm_id,
    )

    if auth_client.access_token is not None:
        access_token = auth_client.access_token

    if auth_client.realm_id is None:
        raise ValueError('Realm id not specified.')
    """[summary]
    
    """
    
    if settings.ENVIRONMENT == 'production':
        base_url = settings.QBO_BASE_PROD
    else:
        base_url =  settings.QBO_BASE_SANDBOX

    route = get_route(request_type, realm_id)
    url = '{0}{1}'.format(base_url, route)
    auth_header = 'Bearer {0}'.format(access_token)
    headers = {
        'Authorization': auth_header, 
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
    response = requests.request(request_method, url, headers=headers, data=payload)
    # If the access_token is expired, we need to refresh it and update the same in database
    if response.status_code == 401:
        auth_client.refresh()
        qbo_details.access_token = auth_client.access_token
        qbo_details.refresh_token = auth_client.refresh_token
        qbo_details.save()
        response = requests.request(request_method, url, headers=headers, data=payload)

    return response


def get_route(request_type,realm_id):
    route_dict = {
        "company_info" : F"/v3/company/{realm_id}/companyinfo/{realm_id}",
        "query_an_account" : F"/v3/company/{realm_id}/query?query=select * from Account where Metadata.CreateTime > '2014-12-31'&minorversion=63",
        "create_an_account" : F"/v3/company/{realm_id}/account?minorversion=63",
    }
    route = route_dict[request_type]
    return route