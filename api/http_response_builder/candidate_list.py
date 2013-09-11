from http_response_builder import HTTP_Response_Builder
from param_definition.parameter import Parameter, Date_Time_Parameter_Type
from datetime import datetime
from model.db_session import DB_Session_Factory
from model.interview import Interview
from sqlalchemy import func
import json

class Candidate_List_HTTP_Response_Builder(HTTP_Response_Builder):
    date = Parameter('date', required = False, default = datetime.now(), parameter_type = Date_Time_Parameter_Type)

    @staticmethod
    def avg_score(scores_string):
        avg_score = 0
        num_scores = 0
        if scores_string is None:
            return 0
        for score in scores_string.split(','):
            score = float(score)
            if (score > 0):
                avg_score = (avg_score * num_scores + score)/(num_scores + 1)
                num_scores += 1
        return avg_score
    

    def print_body(self):
        db_session = DB_Session_Factory.get_db_session()
        interviewees = []
        for interviewee_info in db_session.query(func.group_concat(Interview.technical_score), func.group_concat(Interview.cultural_score), Interview.candidate_name).group_by(Interview.candidate_name).filter(func.date(Interview.start_time) == func.date(self.date)).all():
            [tech_scores, cultural_scores, candidate_name] = interviewee_info
            avg_tech_score = Candidate_List_HTTP_Response_Builder.avg_score(tech_scores)
            avg_cultural_score= Candidate_List_HTTP_Response_Builder.avg_score(cultural_scores)
            status = 'unknown'
            if avg_tech_score > 2.5 and avg_cultural_score > 2.5:
                status = 'success'
            elif avg_tech_score is not 0 and avg_cultural_score is not 0:
                status = 'failure'
            interviewees.append({'candidate_name' : candidate_name, 'status' : status})
        final_output_dict = {'candidates' : interviewees, 'date' : self.date.strftime("%s")}
        print json.dumps(final_output_dict)
