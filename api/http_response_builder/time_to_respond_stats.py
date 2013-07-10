from http_response_builder import HTTP_Response_Builder
from param_definition.parameter import Parameter, Date_Time_Parameter_Type
from datetime import datetime, timedelta

from model.db_session import DB_Session_Factory
from model.interview import Interview
from model.interviewer import Interviewer
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
        interviewers = {}
        for interview in db_session.query(Interview).filter(Interview.start_time > self.earliest_ts, Interview.end_time < self.latest_ts).yield_per(5):
            if interviewers.get(interview.interviewer_email, None) is None:
                interviewers[interview.interviewer_email] = db_session.query(Interviewer).get(interview.interviewer_email).dict_representation()
                interviewers[interview.interviewer_email]['num_interviews'] = 0
            else:
                interviewers[interview.interviewer_email]['num_interviews'] += 1
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
        interviewers_array = []
        max_num_interviews = -1
        for email, info_dict in interviewers.iteritems():
            info_dict['email'] = email
            interviewers_array.append(info_dict)
            if info_dict['num_interviews'] > max_num_interviews:
                max_num_interviews = info_dict['num_interviews']
        for interviewer_info in interviewers_array:
            num_good = 0
            num_bad = 0
            for bucket in self.buckets:
                num_interviews = len(bucket['interviews'].get(interviewer_info['email'], []))
                if bucket['range'] != 'other' and bucket['range'][1] <= 30:
                    num_good += num_interviews
                else:
                    num_bad += num_interviews
            fudge = (max_num_interviews - interviewer_info['num_interviews'])/2.0
            num_good += fudge
            num_bad += fudge
            interviewer_info['score'] = num_good/num_bad
        interviewers_array.sort(key=lambda interviewer_info: interviewer_info['score'], reverse=True)
        print json.dumps({'interviewers' : interviewers_array, 'buckets' : self.buckets})
