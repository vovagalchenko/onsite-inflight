from handle_sms import Handle_SMS_HTTP_Response_Builder
from model.db_session import DB_Session_Factory
from model.interviewer import Interviewer
import re
from string import strip, lower

class Handle_Opt_In_SMS_HTTP_Response_Builder(Handle_SMS_HTTP_Response_Builder):

    @staticmethod
    def parse_opt_in(message):
        message = strip(message)
        match = re.match("^([^:]*):\s*([a-zA-Z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-zA-Z0-9!#$%&'*+/=?^_`{|}~-]+)*@[Bb][Oo][Xx]\.[Cc][Oo][Mm])$", message)
        result = None
        if match is not None:
            name = match.group(1)
            email = lower(match.group(2))
            result = {'name' : name, 'email' : email}
        return result

    def process_sms(self):
        opt_in_data = Handle_Opt_In_SMS_HTTP_Response_Builder.parse_opt_in(self.sms_body)
        response_msg = None
        if opt_in_data is None:
            response_msg = "Your message is formatted incorrectly. The format is: <name>:<box_email>"
        else:
            self.from_phone_number = self.from_phone_number[2:]
            db_session = DB_Session_Factory.get_db_session()
            opt_in = Interviewer.get_interviewer_by_phone_number(self.from_phone_number)
            if opt_in is None:
                opt_in = Interviewer(opt_in_data['email'], opt_in_data['name'], self.from_phone_number)
                db_session.add(opt_in)
                response_msg = "Thank you for registering your information with Onsite Inflight."
            else:
                opt_in.email = opt_in_data['email']
                opt_in.name = opt_in_data['name']
                response_msg = "I've updated your information as you requested. Thanks."
            db_session.commit()
        return response_msg
