from model.admin_permissions import INTERVIEW_DUMP_PERMISSION_MASK
from model.interview import Interview
from api.http_response_builder.csv_dump.csv_dump import CSV_Dump_HTTP_Response_Builder

class Interviews_Dump_HTTP_Response_Builder(CSV_Dump_HTTP_Response_Builder):
    required_admin_permissions = INTERVIEW_DUMP_PERMISSION_MASK
    table_to_dump = Interview
