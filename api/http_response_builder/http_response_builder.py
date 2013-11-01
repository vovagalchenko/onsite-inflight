from param_definition.parameter import Parameter
from cgi import FieldStorage
import Cookie
import base64
import os
from model.user_model import User
from model.db_session import DB_Session_Factory
import uuid
from datetime import datetime
from lib.conf import CFG
import sys
import json

class HTTP_Response_Builder(object):
    content_type = 'application/json'
    params_dump = {}
    requires_authentication = True
    required_admin_permissions = 0x0

    def __init__(self, params_storage):
        try:
            for key in params_storage.keys():
                self.params_dump[key] = params_storage[key].value
        except TypeError:
            # FieldStorage throws a type error when trying to iterate it if no params are passed in... wtf
            pass
        for param_name in dir(self):
            param_definition = getattr(self, param_name)
            if not isinstance(param_definition, Parameter):
                continue
            param_value = param_definition.get_value(params_storage.getvalue(param_definition.name))
            setattr(self, param_name, param_value)

    def get_authenticated_user(self):
        if not CFG.get_instance().is_live():
            db_session = DB_Session_Factory.get_db_session()
            return db_session.query(User).get("vova@box.com")
        try:
            cookie_string = os.environ['HTTP_COOKIE']
            cookie = Cookie.SimpleCookie(cookie_string)
            session_cookie = cookie['session_id'].value
        except (Cookie.CookieError, KeyError):
            session_cookie = None
        result = None
        return User.user_for_session_cookie(session_cookie)

    def is_user_not_authorized(self, authenticated_user):
        return authenticated_user is not None and (authenticated_user.admin_permissions & self.required_admin_permissions) != self.required_admin_permissions
        
    def print_headers(self, authenticated_user):
        if (authenticated_user is None and self.requires_authentication) or self.is_user_not_authorized(authenticated_user):
            print "Status: 403"
            print "Content-Type: application/json"
        else:
            print "Status: 200"
            print "Content-Type: " + self.content_type

    def get_authentication_needed_json(self):
        result = {'error' : 'authn_needed'}
        authn_request = """\
<?xml version="1.0" encoding="UTF-8"?>
<saml2p:AuthnRequest xmlns:saml2p="urn:oasis:names:tc:SAML:2.0:protocol" AssertionConsumerServiceURL="http://onsite-inflight.com/api/post-sso" Destination="https://box.okta.com/app/template_saml_2_0/k5jimobgREMCSHKGRLVB/sso/saml" ForceAuthn="false" ID="%s" IsPassive="false" IssueInstant="%s" ProtocolBinding="urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST" Version="2.0">
<saml2:Issuer xmlns:saml2="urn:oasis:names:tc:SAML:2.0:assertion">http://onsite-inflight.com/api/post-sso</saml2:Issuer>
<saml2p:NameIDPolicy AllowCreate="false" Format="urn:oasis:names:tc:SAML:1.1:nameid-format:unspecified" SPNameQualifier="http://onsite-inflight.com/api/post-sso"/>
</saml2p:AuthnRequest>
""" % (uuid.uuid4().hex, datetime.now().isoformat())
        result['authn_request'] = base64.b64encode(authn_request)
        return result;

    def print_authentication_needed_response(self):
        print json.dumps(self.get_authentication_needed_json())
        

    def print_body_for_user(self, authenticated_user):
        pass

    def print_body(self, authenticated_user):
        authenticated_user = self.get_authenticated_user()
        if self.requires_authentication is True and authenticated_user is None:
            self.print_authentication_needed_response()
        else:
            if self.is_user_not_authorized(authenticated_user):
                result = {'error' : 'not_authorized', 'msg' : authenticated_user.email + " is not authorized to perform this action."}
                print json.dumps(result)
            else:
                self.print_body_for_user(authenticated_user)

    def print_response(self):
        authenticated_user = self.get_authenticated_user()
        self.print_headers(authenticated_user)
        print
        self.print_body(authenticated_user)
