from http_response_builder import HTTP_Response_Builder
from param_definition.parameter import Parameter, Date_Time_Parameter_Type
from datetime import datetime

from model.db_session import DB_Session_Factory
from model.optin import Opt_In
import json

class Opt_In_List_HTTP_Response_Builder(HTTP_Response_Builder):
    date = Parameter('date', required = False, default = None, parameter_type = Date_Time_Parameter_Type)
    requires_authn = False

    def print_body(self):
        opt_ins = []
        for opt_in in Opt_In.get_opt_ins_after_date(self.date):
            opt_ins.append(opt_in.dict_representation())
        print json.dumps(opt_ins)
