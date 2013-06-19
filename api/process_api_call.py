#!/usr/bin/python

from http_response_builder import *
from os import environ
from urlparse import parse_qs
import re
import cgi
import json
import sys

end_points = {   
    'candidate_list' : candidate_list.Candidate_List_HTTP_Response_Builder,
    'candidate_detail' : candidate_detail.Candidate_Detail_HTTP_Response_Builder,
    'post-sso' : post_sso.Post_SSO_HTTP_Response_Builder,
    'handle_sms' : handle_sms.Handle_SMS_HTTP_Response_Builder
}

request_uri = environ.get('REQUEST_URI', '')
match = re.match('\/api\/(.*?)(\?|$)', request_uri);
endpoint = None
if match is not None:
    endpoint = match.group(1)

params_storage = cgi.FieldStorage()
try:
    response_builder = end_points[endpoint](params_storage)
# This 'except' is meant to only catch exceptions that are thrown when passed in
# arguments are insufficient or inappropriate. Probably should create a subclass
# of ValueError for this purpose, but it's not critical right now.
except ValueError as error:
    sys.stderr.write(str(error))
    print "Content-Type: application/json"
    print
    error_dict = {'error' : str(error)}
    print json.dumps(error_dict)
else:
    response_builder.print_headers()
    print
    auth_check_result = response_builder.check_auth()
    if auth_check_result is not None:
        print json.dumps(auth_check_result)
    else:
        response_builder.print_body()