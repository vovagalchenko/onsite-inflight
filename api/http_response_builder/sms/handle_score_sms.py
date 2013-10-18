from handle_sms import Handle_SMS_HTTP_Response_Builder
from model.user_model import User
from model.db_session import DB_Session_Factory
from model.interviewer import Interviewer
import re
from string import strip, lower
from datetime import datetime, timedelta

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
        if message == '-':
            result = -1
        else:
            match = re.match('^([1-4]|one|two|three|four)\s*(\+|\-)?$', message)
            result = None
            if match is not None:
                number = int(Handle_Score_SMS_HTTP_Response_Builder.number_map.get(match.group(1), match.group(1)))
                modifier = Handle_Score_SMS_HTTP_Response_Builder.modifier_map.get(match.group(2), 0)
                result = number + modifier
        return result

    @staticmethod
    def parse_hiring_recommendation(message):
        message = strip(lower(message))
        result = None
        if message == "yes":
            result = 1
        elif message == "no":
            result = 0
        elif message == "-":
            result = -2
        return result

    def process_sms(self):
        self.from_phone_number = self.from_phone_number[2:]
        self.to_phone_number = self.to_phone_number[2:]
        db_session = DB_Session_Factory.get_db_session()
        interviewer = Interviewer.get_interviewer_by_phone_number(self.from_phone_number)
        interview = None
        response_msg = "Thanks for your feedback"
        if interviewer is None:
            response_msg = "I don't know who you are or what you want from me."
        else:
            interview = interviewer.get_most_recently_completed_interview(self.to_phone_number, for_update = True)
            if interview is None:
                response_msg = "You haven't done an interview recently so we have nothing to talk about."

        if interview is not None and interview.technical_score is None and not interview.is_coffee_break():
            # The user should be trying to send in the technical score.
            score = Handle_Score_SMS_HTTP_Response_Builder.parse_score(self.sms_body)
            if score is None:
                response_msg = "Invalid technical score. Valid input is 1, 2, 3, 4 or '-' if you don't have a score to give. You can use +/- for scores. Please try again."
            else:
                interview.technical_score = score
                response_msg = "What's the cultural score?"
        elif interview is not None and interview.cultural_score is None:
            # The user should be trying to send in the cultural score.
            score = Handle_Score_SMS_HTTP_Response_Builder.parse_score(self.sms_body)
            if score is None:
                response_msg = "Invalid cultural score. Valid input is 1, 2, 3, 4 or '-' if you don't have a score to give. You can use +/- for scores. Please try again."
            else:
                interview.cultural_score = score
                response_msg = "Would you recommend hiring this person?"
        elif interview is not None and interview.hire == -1:
            # The user should be trying to send in the hiring recommendation
            hiring_recommendation = Handle_Score_SMS_HTTP_Response_Builder.parse_hiring_recommendation(self.sms_body)
            if hiring_recommendation is None:
                response_msg = "Invalid hiring recommendation. Valid input is yes, no or '-' if you don't have a recommendation to give."
            else:
                interview.hire = hiring_recommendation
                response_msg = "Thanks. Feel free to send in any notes you have about " + interview.candidate_name + " in subsequent texts."
        elif interview is not None:
            # The user should be trying to send in notes for the interview.
            if interview.notes is None:
                interview.notes = ""
            interview.notes = interview.notes + self.sms_body
            if interview.notes_ts is None or datetime.now() - interview.notes_ts >= timedelta(seconds=3):
                response_msg = "Thanks. Your feedback was added to " + interview.candidate_name + "'s file."
            else:
                response_msg = None
        db_session.commit()
        return response_msg
