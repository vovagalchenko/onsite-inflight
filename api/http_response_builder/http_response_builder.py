from param_definition.parameter import Parameter
from cgi import FieldStorage
import Cookie
import base64
import os
from user_model import User
import uuid
from datetime import datetime

class HTTP_Response_Builder():
    requires_authn = False
    content_type = 'application/json'
    params_dump = {}

    def __init__(self, params_storage):
        for key in params_storage.keys():
            self.params_dump[key] = params_storage[key].value
        for param_name in self.__class__.__dict__.keys():
            param_definition = getattr(self, param_name)
            if not isinstance(param_definition, Parameter):
                continue
            param_value = param_definition.get_value(params_storage.getvalue(param_definition.name))
            setattr(self, param_name, param_value)

    def check_auth(self):
        if not self.requires_authn:
            return None

        try:
            cookie_string = os.environ['HTTP_COOKIE']
            cookie = Cookie.SimpleCookie(cookie_string)
            session_cookie = cookie['session_id'].value
        except (Cookie.CookieError, KeyError):
            session_cookie = None
        result = None
        if session_cookie is None or User.session_is_active(session_cookie) is False:
            result = {'error' : 'authn_needed'}
            authn_request = """\
<?xml version="1.0" encoding="UTF-8"?>
<saml2p:AuthnRequest xmlns:saml2p="urn:oasis:names:tc:SAML:2.0:protocol" AssertionConsumerServiceURL="http://onsite-inflight.com/api/post-sso" Destination="https://box.okta.com/app/template_saml_2_0/k5jimobgREMCSHKGRLVB/sso/saml" ForceAuthn="false" ID="%s" IsPassive="false" IssueInstant="%s" ProtocolBinding="urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST" Version="2.0">
    <saml2:Issuer xmlns:saml2="urn:oasis:names:tc:SAML:2.0:assertion">http://onsite-inflight.com/api/post-sso</saml2:Issuer>
    <saml2p:NameIDPolicy AllowCreate="false" Format="urn:oasis:names:tc:SAML:1.1:nameid-format:unspecified" SPNameQualifier="http://onsite-inflight.com/api/post-sso"/>
</saml2p:AuthnRequest>
""" % (uuid.uuid4().hex, datetime.now().isoformat())
            result['authn_request'] = base64.b64encode(authn_request)
        return result

    def print_headers(self):
        print "Content-Type: " + self.content_type

    def print_body(self):
        pass

    def print_response(self):
        self.print_headers()
        print
        self.print_body()
