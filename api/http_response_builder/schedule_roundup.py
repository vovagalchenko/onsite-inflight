from apiclient.errors import HttpError
from oauth2client.client import AccessTokenRefreshError
from http_response_builder import HTTP_Response_Builder
from param_definition.parameter import Parameter, Date_Time_Parameter_Type, String_Parameter_Type, Integer_Parameter_Type
from datetime import datetime, timedelta, date
from model.db_session import DB_Session_Factory
from model.interview import Interview
from sqlalchemy import func
from lib.calendar import Google_Calendar, google_ts_to_datetime, LOS_ANGELES_TZ, datetime_to_google_ts
from model.admin_permissions import ROUNDUP_SCHEDULING_PERMISSION_MASK
import sys
import json
import urllib

class Schedule_Roundup_HTTP_Response_Builder(HTTP_Response_Builder):
    required_admin_permissions = ROUNDUP_SCHEDULING_PERMISSION_MASK
    roundup_start_date = Parameter('start_date', required = True, parameter_type = Date_Time_Parameter_Type)
    roundup_length = Parameter('length', required = True, parameter_type = Integer_Parameter_Type)
    candidate_name = Parameter('candidate_name', required = True, parameter_type = String_Parameter_Type)

    def print_body_for_user(self, authenticated_user):
        db_session = DB_Session_Factory.get_db_session()
        panel = []
        for interview in db_session.query(Interview).filter(Interview.candidate_name == self.candidate_name, func.date(Interview.start_time) == func.date(datetime.now())):
            panel.append({
                'email' : interview.interviewer_email,
                'optional' : True,
                'responseStatus' : 'needsAction'
            })
        if len(panel) is 0:
            print json.dumps({'error' : 'Nobody to invite to roundup for ' + self.candidate_name})
        else:
            event = {}
            event['organizer'] = {'self' : True}
            event['location'] = '4440-2-6 Nuthouse'
            event['start'] = datetime_to_google_ts(self.roundup_start_date)
            event['end'] = datetime_to_google_ts(self.roundup_start_date + timedelta(minutes = self.roundup_length))
            event['summary'] = "Roundup for " + self.candidate_name
            event['guestsCanInviteOthers'] = True
            event['attendees'] = panel
            now_date = date.today()
            event['description'] = "https://onsite-inflight.com/#" + str(now_date.year) + "-" + ("%02d"%now_date.month) + "-" + ("%02d"%now_date.day) + "/" + urllib.quote_plus(self.candidate_name)
            calendar = Google_Calendar.get_calendar()
            try:
                calendar.service.events().insert(calendarId = "box.com_k7897kemv3a14qldj8s546jfig@group.calendar.google.com", body = event, sendNotifications=True).execute(calendar.http)
                print json.dumps({'status' : 'success'})
            except HttpError as e:
                error_response = json.dumps({"error" : "Google calendar http error: " + e.content})
                sys.stderr.write(error_response)
                print error_response
            except AccessTokenRefreshError:
                print json.dumps({"error" : "The Google calendar credentials have been revoked or expired"})
