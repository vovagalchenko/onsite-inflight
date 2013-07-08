from http_response_builder import HTTP_Response_Builder
from param_definition.parameter import Parameter, Date_Time_Parameter_Type
from datetime import datetime, timedelta

from model.db_session import DB_Session_Factory
from model.interview import Interview
from sqlalchemy import func
import json

class Time_To_Respond_Stats_HTTP_Response_Builder(HTTP_Response_Builder):
    requires_authn = False
    earliest_ts = Parameter('earliest_ts', required = False, default = datetime.now() - timedelta(days=30), parameter_type = Date_Time_Parameter_Type)
    latest_ts = Parameter('earliest_ts', required = False, default = datetime.now(), parameter_type = Date_Time_Parameter_Type)

    buckets = [{
        'range' : [0, 5],
        'interviews' : {},
    },
    {
        'range' : [5, 10],
        'interviews' : {},
    },
    {
        'range' : [10, 15],
        'interviews' : {},
    },
    {
        'range' : [15, 20],
        'interviews' : {},
    },
    {
        'range' : [20, 25],
        'interviews' : {},
    },
    {
        'range' : [25, 30],
        'interviews' : {},
    },
    {
        'range' : [30, 35],
        'interviews' : {},
    },
    {
        'range' : [35, 45],
        'interviews' : {},
    },
    {
        'range' : [45, 50],
        'interviews' : {},
    },
    {
        'range' : [50, 55],
        'interviews' : {},
    },
    {
        'range' : [55, 60],
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
            interviews[interview.interviewer_email] = []
        interviews[interview.interviewer_email].append(interview.dict_representation())

    def print_body(self):
        db_session = DB_Session_Factory.get_db_session()
        interviewees = []
        for interview in db_session.query(Interview).filter(Interview.start_time > self.earliest_ts, Interview.end_time < self.latest_ts).yield_per(5):
            if interview.cultural_score_ts is None or interview.end_time is None:
                seconds_to_respond = -1;
            else:
                seconds_to_respond = (interview.cultural_score_ts - interview.end_time).total_seconds() - 5*60; # we only send out a message 5 minutes after interview ending
            for bucket in self.buckets:
                if bucket['range'] == 'other':
                    Time_To_Respond_Stats_HTTP_Response_Builder.insert_interview_into_bucket(interview, bucket)
                    break
                elif seconds_to_respond > (bucket['range'][0]*60) and seconds_to_respond <= (bucket['range'][1]*60):
                    Time_To_Respond_Stats_HTTP_Response_Builder.insert_interview_into_bucket(interview, bucket)
                    break
                else:
                    continue
        print json.dumps(self.buckets)
