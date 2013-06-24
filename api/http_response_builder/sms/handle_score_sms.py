from handle_sms import Handle_SMS_HTTP_Response_Builder
from model.user_model import User
from model.db_session import DB_Session_Factory
from model.interviewer import Interviewer
import re
from string import strip, lower

class Handle_Score_SMS_HTTP_Response_Builder(Handle_SMS_HTTP_Response_Builder):
    number_map = {
        "one" : 1,
        "two" : 2,
        "three" : 3,
        "four" : 4,
    }

    modifier_map = {
        "+" : .25,
        "-" : -.25
    }

    @staticmethod
    def parse_score(message):
        message = strip(lower(message))
        match = re.match('^([1-4]|one|two|three|four)\s*(\+|\-|$)', message)
        result = None
        if match is not None:
            number = int(Handle_Score_SMS_HTTP_Response_Builder.number_map.get(match.group(1), match.group(1)))
            modifier = Handle_Score_SMS_HTTP_Response_Builder.modifier_map.get(match.group(2), 0)
            result = number + modifier
        return result

    def process_sms(self):
        self.phone_number = self.phone_number[2:]
        db_session = DB_Session_Factory.get_db_session()
        interviewer = Interviewer.get_interviewer_by_phone_number(self.phone_number)
        interview = interviewer.get_most_recently_completed_interview()

        response_msg = "Thanks for your feedback!"
        if interview.technical_score is None and not interview.is_coffee_break():
            score = Handle_Score_SMS_HTTP_Response_Builder.parse_score(self.sms_body)
            if score is None:
                response_msg = "Invalid technical score. Valid input is 1, 2, 3, 4 or one, two, three, four. You can also use +/-. Please try again."
            else:
                interview.technical_score = score
                response_msg = "What's the cultural score?"
        elif interview.cultural_score is None:
            score = Handle_Score_SMS_HTTP_Response_Builder.parse_score(self.sms_body)
            if score is None:
                response_msg = "Invalid cultural score. Valid input is 1, 2, 3, 4 or one, two, three, four. You can also use +/-. Please try again."
            else:
                interview.cultural_score = score
        db_session.commit()
        return response_msg
