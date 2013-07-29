from http_response_builder import HTTP_Response_Builder
from param_definition.parameter import Parameter, Date_Time_Parameter_Type, Boolean_Parameter_Type
from model.db_session import DB_Session_Factory
from model.interviewer import Interviewer
from lib.calendar import get_resource_id_for_interviewer
import json
import sys
import os

class Calendar_Notification_HTTP_Response_Builder(HTTP_Response_Builder):
    def check_auth(self):
        return None

    def print_body(self):
        resource_state = os.environ.get('HTTP_X_GOOG_RESOURCE_STATE', None)
        resource_id = os.environ.get('HTTP_X_GOOG_RESOURCE_ID', None)
        channel_id = os.environ.get('HTTP_X_GOOG_CHANNEL_ID', None)
        if resource_state == "exists" and resource_id is not None and channel_id is not None:
            db_session = DB_Session_Factory.get_db_session()
            interviewer = db_session.query(Interviewer).filter(Interviewer.push_notification_id == resource_id).first()
            if get_resource_id_for_interviewer(interviewer) != channel_id:
                sys.stderr.write("Received notification for an unknown channel id: " + channel_id)
            elif interviewer is None:
                sys.stderr.write("Received notification for an unknown resource id: " + resource_id)
            else:
                interviewer.needs_calendar_sync = 1
                db_session.add(interviewer)
                db_session.commit()
