from http_response_builder import HTTP_Response_Builder
from param_definition.parameter import Parameter, Date_Time_Parameter_Type, Boolean_Parameter_Type
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

    @staticmethod
    def insert_interview_into_bucket(interview, bucket):
        interviews = bucket['interviews']
        if interviews.get(interview.interviewer_email, None) is None:
            interviews[interview.interviewer_email] = []
        interviews[interview.interviewer_email].append(interview.dict_representation())

    def print_body(self):
        db_session = DB_Session_Factory.get_db_session()
        interviewers = {}
        for interview in db_session.query(Interview).filter(Interview.start_time > self.earliest_ts, Interview.end_time < self.latest_ts, Interview.cultural_score != None).order_by(Interview.start_time).yield_per(5):
            if interviewers.get(interview.interviewer_email, None) is None:
                interviewers[interview.interviewer_email] = db_session.query(Interviewer).get(interview.interviewer_email).dict_representation()
                interviewers[interview.interviewer_email]['interviews'] = []
            interviewers[interview.interviewer_email]['interviews'].append(interview.dict_representation())
        interviewers_array = []
        print json.dumps(interviewers)
