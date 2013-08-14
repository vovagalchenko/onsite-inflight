from http_response_builder import HTTP_Response_Builder
from param_definition.parameter import Parameter, Date_Time_Parameter_Type
from datetime import datetime

from model.db_session import DB_Session_Factory
from model.interviewer import Interviewer
import json

class Opt_In_List_HTTP_Response_Builder(HTTP_Response_Builder):
    date = Parameter('date', required = False, default = datetime.now(), parameter_type = Date_Time_Parameter_Type)

    def check_auth(self):
        return None

    def print_body(self):
        opt_ins = []
        db_session = DB_Session_Factory.get_db_session()
        for interviewer in db_session.query(Interviewer).filter(Interviewer.created > self.date):
            interviewer_dict = interviewer.dict_representation()
            interviewer_dict['phone_number'] = interviewer.phone_number
            interviewer_dict['nickname'] = interviewer.nickname()
            opt_ins.append(interviewer_dict)
        print json.dumps(opt_ins)
