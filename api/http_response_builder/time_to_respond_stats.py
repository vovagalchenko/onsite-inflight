from http_response_builder import HTTP_Response_Builder
from param_definition.parameter import Parameter, Date_Time_Parameter_Type
from datetime import datetime

from model.db_session import DB_Session_Factory
from model.interview import Interview
from sqlalchemy import func
import json

class Time_To_Respond_Stats_HTTP_Response_Builder(HTTP_Response_Builder):
    requires_authn = False
    buckets = [{
        'range' : [0, 5],
        'interviews' : {},
    },
    {
        'range' : [5, 15],
        'interviews' : {},
    },
    {
        'range' : [15, 30],
        'interviews' : {},
    },
    {
        'range' : [30, 45],
        'interviews' : {},
    },
    {
        'range' : [45, 60],
        'interviews' : {},
    },
    {
        'range' : 'other',
        'interviews' : {},
    }]

    @staticmethod
    def insert_interview_into_bucket(interview, bucket):
        interviews = bucket['interviews']
        if interviews.get(interview.interviewer_email, None) is None:
            interviews[interview.interviewer_email] = 0
        interviews[interview.interviewer_email] += 1

    def print_body(self):
        db_session = DB_Session_Factory.get_db_session()
        interviewees = []
        for interview in db_session.query(Interview).yield_per(5):
            for bucket in self.buckets:
                if bucket['range'] == 'other':
                    Time_To_Respond_Stats_HTTP_Response_Builder.insert_interview_into_bucket(interview, bucket)
                if interview.cultural_score_ts is None:
                    continue
                seconds_to_respond = (interview.cultural_score_ts - interview.end_time).total_seconds() - 5*60; # we only send out a message 5 minutes after interview ending
                if seconds_to_respond > bucket['range'][0]*60 and seconds_to_respond <= bucket['range'][1]*60:
                    Time_To_Respond_Stats_HTTP_Response_Builder.insert_interview_into_bucket(interview, bucket)
                else:
                    continue
        print json.dumps(self.buckets)
