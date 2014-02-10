from model.admin_permissions import INTERVIEW_DUMP_PERMISSION_MASK
from model.interview import Interview
from model.candidate import Candidate
from model.db_session import DB_Session_Factory
from api.http_response_builder.csv_dump.csv_dump import CSV_Dump_HTTP_Response_Builder
import csv, sys

class Interviews_Dump_HTTP_Response_Builder(CSV_Dump_HTTP_Response_Builder):
    required_admin_permissions = INTERVIEW_DUMP_PERMISSION_MASK

    def print_body_for_user(self, authenticated_user):
        csv_writer = csv.writer(sys.stdout)
        db_session = DB_Session_Factory.get_db_session()
        interview_fields = [column.name for column in Interview.__mapper__.columns]
        candidate_fields = ['position']
        csv_writer.writerow(interview_fields + candidate_fields)
        [ csv_writer.writerow([getattr(interview, interview_field) for interview_field in interview_fields] + [getattr(candidate, candidate_field) for candidate_field in candidate_fields]) for interview, candidate in db_session.query(Interview, Candidate).filter(Interview.candidate_name == Candidate.candidate_name) ]
