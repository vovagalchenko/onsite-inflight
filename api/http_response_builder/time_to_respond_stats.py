from http_response_builder import HTTP_Response_Builder
from param_definition.parameter import Parameter, Date_Time_Parameter_Type, Boolean_Parameter_Type
from datetime import datetime, timedelta

from model.db_session import DB_Session_Factory
from model.interview import Interview
from model.interviewer import Interviewer
from sqlalchemy import func
import json

class Time_To_Respond_Stats_HTTP_Response_Builder(HTTP_Response_Builder):
    earliest_ts = Parameter('earliest_ts', required = False, default = datetime.now() - timedelta(days=30), parameter_type = Date_Time_Parameter_Type)
    latest_ts = Parameter('earliest_ts', required = False, default = datetime.now(), parameter_type = Date_Time_Parameter_Type)
    include_non_responders = Parameter('include_non_responders', required = False, default = False, parameter_type = Boolean_Parameter_Type)
    requires_authentication = False

    def print_body_for_user(self, authenticated_user):
        db_session = DB_Session_Factory.get_db_session()
        self.earliest_ts = self.earliest_ts.date()
        interviewers = {}
        for interview_data in db_session.query(Interview, Interviewer).join(Interviewer, Interview.interviewer_email == Interviewer.email).filter(Interview.start_time > self.earliest_ts, Interview.end_time < self.latest_ts).yield_per(5):
            interview,interviewer = interview_data
            if self.include_non_responders is False and interview.cultural_score is None:
                continue
            if interviewers.get(interview.interviewer_email, None) is None:
                interviewers[interview.interviewer_email] = interviewer.dict_representation()
                interviewers[interview.interviewer_email]['interviews'] = []
            interviewers[interview.interviewer_email]['interviews'].append(interview.dict_representation(show_scores = False))
        interviewers_array = []
        print json.dumps(interviewers)
