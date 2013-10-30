from api.http_response_builder.http_response_builder import HTTP_Response_Builder
from api.http_response_builder.param_definition.parameter import Parameter, Date_Time_Parameter_Type
from datetime import datetime
from model.db_session import DB_Session_Factory
from model.user_model import User
from model.employee import Employee
from model.reimbursement import Reimbursement
from api.http_response_builder.param_definition.parameter import Parameter, Integer_Parameter_Type
from sqlalchemy import func
import sys
import json

class Update_Reimbursements_HTTP_Response_Builder(HTTP_Response_Builder):
    requested_gym_reimbursement = Parameter('gym', required = True, parameter_type = Integer_Parameter_Type)
    requested_mobile_reimbursement = Parameter('mobile', required = True, parameter_type = Integer_Parameter_Type)
    
    def print_body_for_user(self, authenticated_user):
        db_session = DB_Session_Factory.get_db_session()
        employee = db_session.query(Employee).get(authenticated_user.email)
        if employee is None:
            employee = Employee(authenticated_user.email)
            db_session.add(employee)
            sys.stderr.write(employee.email)
        max_amounts = {}
        for reimbursement in db_session.query(Reimbursement).all():
            max_amounts[reimbursement.id] = reimbursement.max_amount
        error = None
        if self.requested_gym_reimbursement > max_amounts['gym'] or self.requested_mobile_reimbursement > max_amounts['mobile']:
            error = "You are asking too much."
        else:
            employee.gym = self.requested_gym_reimbursement
            employee.mobile = self.requested_mobile_reimbursement
        db_session.commit()
        final_output_dict = {}
        if error is not None:
            final_output_dict['error'] = error
        else:
            final_output_dict['status'] = 'ok';
        print json.dumps(final_output_dict)
