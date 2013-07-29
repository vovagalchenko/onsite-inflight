#!/usr/bin/python

from http_response_builder import *
from http_response_builder.sms import *
from os import environ
from urlparse import parse_qs
import re
import cgi
import json
import sys

end_points = {   
    'candidate_list' : candidate_list.Candidate_List_HTTP_Response_Builder,
    'candidate_detail' : candidate_detail.Candidate_Detail_HTTP_Response_Builder,
    'teammates' : teammates.Teammates_HTTP_Response_Builder,
    'post-sso' : post_sso.Post_SSO_HTTP_Response_Builder,
    'handle_score_sms' : handle_score_sms.Handle_Score_SMS_HTTP_Response_Builder,
    'handle_opt_in_sms' : handle_optin_sms.Handle_Opt_In_SMS_HTTP_Response_Builder,
    'opt_in_list' : opt_in_list.Opt_In_List_HTTP_Response_Builder,
    'time_to_respond_stats' : time_to_respond_stats.Time_To_Respond_Stats_HTTP_Response_Builder,
    'scores_by_time_stats' : scores_by_time_stats.Scores_By_Time_Stats_HTTP_Response_Builder,
    'calendar_notification' : calendar_notification.Calendar_Notification_HTTP_Response_Builder
}

request_uri = environ.get('REQUEST_URI', '')
match = re.match('\/api\/(.*?)(\?|$)', request_uri);
endpoint = None
if match is not None:
    endpoint = match.group(1)

try:
    response_builder_class = end_points.get(endpoint, None)
    if response_builder_class is None:
        output_str = json.dumps({'error' : 'invalid api endpoint: ' + str(endpoint)})
        sys.stderr.write(output_str)
        print "Content-Type: application/json"
        print
        print output_str
        exit()
    params_storage = cgi.FieldStorage()
    response_builder = response_builder_class(params_storage)
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
