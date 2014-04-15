from http_response_builder import HTTP_Response_Builder
from param_definition.parameter import Parameter, Date_Time_Parameter_Type, Integer_Parameter_Type
from datetime import datetime, timedelta
from sets import Set

from model.db_session import DB_Session_Factory
from model.interview import Interview
from model.interviewer import Interviewer
from sqlalchemy import func
import json

class Time_Invested_HTTP_Response_Builder(HTTP_Response_Builder):
    num_days = Parameter('num_weeks', required = False, default = 15*7, parameter_type = Integer_Parameter_Type)
    requires_authentication = False

    def print_body_for_user(self, authenticated_user):
        now = datetime.now()
        end_date = now - timedelta(hours=now.hour, minutes=now.minute, seconds=now.second, microseconds=now.microsecond)
        start_date = end_date - timedelta(days=self.num_days)
        db_session = DB_Session_Factory.get_db_session()
        time_spent = {}
        interviewer_emails = []
        for time_spent_info in db_session.query(func.date(Interview.start_time), Interview.interviewer_email, func.sum(func.time_to_sec(func.timediff(Interview.end_time, Interview.start_time)))).group_by(func.date(Interview.start_time), Interview.interviewer_email).filter(Interview.start_time > start_date, Interview.end_time < end_date).all():
            [date, email, secs_spent] = time_spent_info
            date_str = date.isoformat()
            if time_spent.get(date_str) is None:
                time_spent[date_str] = {}
            time_spent[date_str][email] = int(secs_spent)
            interviewer_emails.append(email)
        interviewers = {}
        for interviewer in db_session.query(Interviewer).filter(Interviewer.email.in_(interviewer_emails)).all():
            interviewers[interviewer.email] = interviewer.dict_representation()
        print json.dumps({
            'time_spent' : time_spent,
            'interviewers' : interviewers
        })
