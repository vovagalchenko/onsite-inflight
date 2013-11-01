import re
from os import environ

def get_api_endpoint():
    request_uri = environ.get('REQUEST_URI', '') 
    match = re.match('\/api\/(.*?)(\?|$)', request_uri);
    endpoint = None
    if match is not None:
        endpoint = match.group(1)
    return endpoint

