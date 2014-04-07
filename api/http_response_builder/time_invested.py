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
    latest_ts = Parameter('earliest_ts', required = False, default = datetime.now(), parameter_type = Date_Time_Parameter_Type)
    num_weeks = Parameter('num_weeks', required = False, default = 10, parameter_type = Integer_Parameter_Type)
    requires_authentication = False

    def print_body_for_user(self, authenticated_user):
        days_to_subtract = self.latest_ts.weekday() + 2
        if self.latest_ts.weekday() >= 5:
            days_to_subtract = self.latest_ts.weekday()%5
        end_of_week = self.latest_ts - timedelta(days=days_to_subtract, hours=self.latest_ts.hour, minutes=self.latest_ts.minute, seconds=self.latest_ts.second)
        db_session = DB_Session_Factory.get_db_session()
        all_time_spent_info = []
        interviewer_emails_set = Set()
        for i in range(0, self.num_weeks):
            beginning_of_week = end_of_week - timedelta(days=7)
            beginning_of_week_string = beginning_of_week.isoformat()
            time_spent_dict = {}
            for time_spent_info in db_session.query(Interview.interviewer_email, func.sum(func.time_to_sec(func.timediff(Interview.end_time, Interview.start_time)))).group_by(Interview.interviewer_email).filter(Interview.start_time > beginning_of_week, Interview.end_time < end_of_week).all():
                [email, secs_spent] = time_spent_info
                time_spent_dict[email] = int(secs_spent)
                interviewer_emails_set.add(email)
            all_time_spent_info.append({
                'week' : beginning_of_week_string,
                'investment' : time_spent_dict
            });
            end_of_week = beginning_of_week
        interviewers = {}
        for interviewer in db_session.query(Interviewer).filter(Interviewer.email.in_(interviewer_emails_set)).all():
            interviewers[interviewer.email] = interviewer.dict_representation()
        print json.dumps({
            'time_invested' : all_time_spent_info,
            'interviewers' : interviewers,
        })
