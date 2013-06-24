from api.http_response_builder.http_response_builder import HTTP_Response_Builder
from api.http_response_builder.param_definition.parameter import Parameter, Base_64_Encoded_XML_Parameter_Type
from lib.logger import log_incoming_sms, log_outgoing_sms
import twilio.twiml

class Handle_SMS_HTTP_Response_Builder(HTTP_Response_Builder):
    requires_authn = False
    phone_number = Parameter('From', required = True)
    sms_body = Parameter('Body', required = True)

    def __init__(self, params_storage):
        super(Handle_SMS_HTTP_Response_Builder, self).__init__(params_storage)
        log_incoming_sms(self.phone_number, self.params_dump)

    def print_headers(self):
        print "Content-Type: application/xml"

    def print_response_message_body(self, response_msg):
        resp = twilio.twiml.Response()
        resp.sms(response_msg)
        print str(resp)
        log_outgoing_sms(self.phone_number, response_msg)
