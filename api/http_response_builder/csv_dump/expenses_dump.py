from model.admin_permissions import REIMBURSEMENT_DUMP_PERMISSION_MASK
from model.employee import Employee
from api.http_response_builder.csv_dump.csv_dump import CSV_Dump_HTTP_Response_Builder

class Expenses_Dump_HTTP_Response_Builder(CSV_Dump_HTTP_Response_Builder):
    required_admin_permissions = REIMBURSEMENT_DUMP_PERMISSION_MASK
    table_to_dump = Employee

    def get_array_to_write_to_csv(self, employee):
        return [employee.email, employee.gym/100.0, employee.mobile/100.0]
