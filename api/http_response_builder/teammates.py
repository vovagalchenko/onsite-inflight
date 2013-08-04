from http_response_builder import HTTP_Response_Builder
from param_definition.parameter import Parameter, Date_Time_Parameter_Type, Boolean_Parameter_Type
from model.db_session import DB_Session_Factory
from model.candidate import Candidate
from model.interviewer_tag import Interviewer_Tag
from model.interviewer import Interviewer
import json
import re
import sys

class Teammates_HTTP_Response_Builder(HTTP_Response_Builder):
    candidate_name = Parameter('candidate_name', required = False)
    tag = Parameter('tag', required = False)

    def check_auth(self):
        return None

    def get_teammates_from_tag(self, tag_string):
        ret_value = []
        db_session = DB_Session_Factory.get_db_session()
        tag = db_session.query(Interviewer_Tag).get(tag_string)
        if tag is not None:
            for interviewer_email in tag.get_interviewers():
                ret_value.append(db_session.query(Interviewer).get(interviewer_email).dict_representation())
        return ret_value

    def print_body(self):
        db_session = DB_Session_Factory.get_db_session()
        
        if self.tag is not None:
            print json.dumps({'tag' : self.tag, 'teammates' : self.get_teammates_from_tag(self.tag)})
        else:
            candidate = db_session.query(Candidate).get(self.candidate_name)
            position = re.sub("^.*?,\s?", "", candidate.position)
            position_list = re.split("[/ ]", position)

            if candidate is None:
                print json.dumps({'candidate_name' : self.candidate_name, 'error' : 'Invalid candidate_name passed in.'})
            else:
                interviewer_list = []
                for position_token in position_list:
                    if position_token == "":
                        continue
                    tag = db_session.query(Interviewer_Tag).get(position_token)
                    if tag is not None:
                        for interviewer_email in tag.get_interviewers():
                            interviewer_list.append(db_session.query(Interviewer).get(interviewer_email).dict_representation())
                        break
                            
                print json.dumps({
                    'candidate_name' : self.candidate_name,
                    'position' : position,
                    'teammates' : interviewer_list
                })
