from http_response_builder import HTTP_Response_Builder
from param_definition.parameter import Parameter, Base_64_Encoded_XML_Parameter_Type
from model.user_model import User

class Post_SSO_HTTP_Response_Builder(HTTP_Response_Builder):
    relay_state = Parameter('RelayState', required = False, default = 'dashboard')
    saml_response = Parameter('SAMLResponse', required = True, parameter_type = Base_64_Encoded_XML_Parameter_Type)
    requires_authentication = False

    def print_forbidden_headers(self):
        print "Status: 403"
    
    def print_headers(self):
        status_code = None
        for status_code_element in self.saml_response.iter("{urn:oasis:names:tc:SAML:2.0:protocol}StatusCode"):
            status_code = status_code_element.get('Value')
            if status_code != 'urn:oasis:names:tc:SAML:2.0:status:Success':
                self.print_forbidden_headers()
                return
        if status_code is None:
            self.print_forbidden_headers()
            return
        
        email = None
        # There really should only be one... but we'll loop through it anyway.
        for email_element in self.saml_response.iter('{urn:oasis:names:tc:SAML:2.0:assertion}NameID'):
            email = email_element.text
        if email is None:
            self.print_forbidden_headers()
            return
        
        user = User.refresh_user_session(email)
        print "Status: 303"
        print "Set-Cookie: session_id=" + user.session_id + "; Domain=onsite-inflight.com; Path=/"
        print "Location: https://onsite-inflight.com/" + self.relay_state
