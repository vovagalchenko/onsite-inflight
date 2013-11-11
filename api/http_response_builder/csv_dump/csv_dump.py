from api.http_response_builder.http_response_builder import HTTP_Response_Builder
from api.http_utils import get_api_endpoint
from model.db_session import DB_Session_Factory
import csv
import sys

class CSV_Dump_HTTP_Response_Builder(HTTP_Response_Builder):
    content_type = 'text/csv'
    requires_authentication = True
    required_admin_permissions = 0xFFFF
    table_to_dump = None

    def print_authentication_needed_response(self):
        authn_needed_json = self.get_authentication_needed_json()
        response = """
<!DOCTYPE html>
<HTML>
    <TITLE>Interview Data Dump</TITLE>
    <SCRIPT type="text/javascript">
        window.onload = function()
        {
            document.getElementById("authn_form").submit();
        };
    </SCRIPT>
<HEAD>
</HEAD>
<BODY>
<FORM id="authn_form" method="POST" action="https://box.okta.com/app/template_saml_2_0/k5jimobgREMCSHKGRLVB/sso/saml">
    <INPUT type="hidden" id="saml_response_input" name="SAMLResponse" value="%s"/>
    <INPUT type="hidden" id="saml_relay_state_input" name="RelayState" value="api/%s"/>
    <INPUT type="submit" value="Submit"/>
</FORM> 
</BODY>
</HTML>
""" % (authn_needed_json['authn_request'], get_api_endpoint())
        print response

    def print_headers(self, authenticated_user):
        if authenticated_user is None or self.is_user_not_authorized(authenticated_user):
        # This is hacky, but we expect the CSV dump api calls to be made directly from the browser.
        # We will send back an authentication form as HTML
            print "Status: 403"
            print "Content-Type: text/html"
        else:
            print "Status: 200"
            print "Content-Type: " + self.content_type
            print "Cache-Control: no-cache, no-store, must-revalidate"
            print "Pragma: no-cache"
            print "Expires: 0"

    def get_array_to_write_to_csv(self, record):
        return [getattr(record, column.name) for column in self.table_to_dump.__mapper__.columns]

    def print_body_for_user(self, authenticated_user):
        csv_writer = csv.writer(sys.stdout)
        db_session = DB_Session_Factory.get_db_session()
        csv_writer.writerow([column.name for column in self.table_to_dump.__mapper__.columns])
        [ csv_writer.writerow(self.get_array_to_write_to_csv(curr)) for curr in db_session.query(self.table_to_dump) ]
