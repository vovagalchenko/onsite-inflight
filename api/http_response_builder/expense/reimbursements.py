from api.http_response_builder.http_response_builder import HTTP_Response_Builder
from api.http_response_builder.param_definition.parameter import Parameter, Date_Time_Parameter_Type
from datetime import datetime
from model.db_session import DB_Session_Factory
from model.user_model import User
from model.employee import Employee
from model.reimbursement import Reimbursement
from sqlalchemy import func
import json

class Reimbursements_HTTP_Response_Builder(HTTP_Response_Builder):
    
    def print_body(self):
        db_session = DB_Session_Factory.get_db_session()
        employee = db_session.query(Employee).get(self.user.email)
        if employee is None:
            employee = Employee(self.user.email)
        reimbursements = []
        for reimbursement in db_session.query(Reimbursement).all():
            reimbursements.append(reimbursement.dict_representation())
        final_output_dict = {'employee' : employee.dict_representation(), 'reimbursement_policy' : reimbursements}
        print json.dumps(final_output_dict)
