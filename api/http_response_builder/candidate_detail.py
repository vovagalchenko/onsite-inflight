from http_response_builder import HTTP_Response_Builder
from param_definition.parameter import Parameter, Date_Time_Parameter_Type, Boolean_Parameter_Type
from model.db_session import DB_Session_Factory
from model.candidate import Candidate

class Candidate_Detail_HTTP_Response_Builder(HTTP_Response_Builder):
    candidate_name = Parameter('candidate_name', required = True)
    date = Parameter('date', required = False, parameter_type = Date_Time_Parameter_Type)
    show_scores = Parameter('show_scores', required = False, default = True, parameter_type = Boolean_Parameter_Type)

    def check_auth(self):
        if self.show_scores is True:
            super(Candidate_Detail_HTTP_Response_Builder, self).check_auth()
        else:
            return None

    def print_body(self):
        db_session = DB_Session_Factory.get_db_session()
        candidate = db_session.query(Candidate).get(self.candidate_name)
        if candidate is None:
            print json.dumps({'candidate_name' : self.candidate_name, 'error' : 'Invalid candidate_name passed in.'})
        else:
            print candidate.json_representation(self.date, show_scores = self.show_scores)
