#!/usr/bin/python

from http_response_builder import *
from http_response_builder.sms import *
from http_response_builder.expense import *
from http_response_builder.csv_dump import *
from urlparse import parse_qs
from http_utils import get_api_endpoint
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
    'calendar_notification' : calendar_notification.Calendar_Notification_HTTP_Response_Builder,
    'reimbursements' : reimbursements.Reimbursements_HTTP_Response_Builder,
    'update_reimbursement' : update.Update_Reimbursements_HTTP_Response_Builder,
    'interviews_dump' : interviews_dump.Interviews_Dump_HTTP_Response_Builder,
    'expenses_dump' : expenses_dump.Expenses_Dump_HTTP_Response_Builder,
    'schedule_roundup' : schedule_roundup.Schedule_Roundup_HTTP_Response_Builder,
    'time_invested' : time_invested.Time_Invested_HTTP_Response_Builder
}

endpoint = get_api_endpoint()
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
    response_builder.print_response()
