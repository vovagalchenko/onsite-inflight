import os
import logging
from pytz import timezone, utc 
from datetime import datetime, timedelta
import re

from lib.conf import CFG

from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import run
from oauth2client.client import AccessTokenRefreshError
import httplib2

from apiclient.discovery import build
from apiclient.errors import HttpError

from model.candidate import Candidate
from model.db_session import DB_Session_Factory

from model.interviewer import Interviewer
from model.interview import Interview

import time

LOS_ANGELES_TZ = "America/Los_Angeles"
DEFAULT_DATE = '1970-01-01T07:00:00-07:00'

def flush_interviews(interviewer, interviews_to_delete, interviews_for_interviewer, from_date, to_date, db_session):
    for interview_to_delete in interviews_to_delete:
        delete_interview(interview_to_delete, db_session)
    phone_number_index = 0 
    phone_numbers = CFG.get_instance().get('twilio', 'from_phone_numbers').split(',')
    latest_existing_interview_start_time = datetime.fromordinal(from_date.toordinal())
    for index, existing_interview in enumerate(interviews_for_interviewer):
        if latest_existing_interview_start_time < existing_interview.start_time:
            latest_existing_interview_start_time = existing_interview.start_time
        if existing_interview.phone_number_to_use is None:
            # Make sure that no two consecutive interviews use the same phone number
            while len(phone_numbers) > 1 and (get_phone_number(interviews_for_interviewer, index - 1) == phone_numbers[phone_number_index] or get_phone_number(interviews_for_interviewer, index + 1) == phone_numbers[phone_number_index]):
                phone_number_index = (phone_number_index + 1)%len(phone_numbers)
            existing_interview.phone_number_to_use = phone_numbers[phone_number_index]
    db_session.flush()
    db_session.commit()
    print "DELETE: " + str(latest_existing_interview_start_time) + " - " + str(to_date)
    for deleted_interview in interviewer.interviews.filter(Interview.start_time > latest_existing_interview_start_time, Interview.start_time < to_date):
        delete_interview(deleted_interview, db_session)
    db_session.flush()
    db_session.commit()

def delete_interview(interview, db_session):
    print "Deleting interview with " + interview.candidate_name
    candidate = interview.candidate
    db_session.delete(interview)
    if not candidate.interviews:
        db_session.delete(candidate)

def google_ts_to_datetime(google_ts):
    last_char = google_ts[-1:]
    tz_offset = 0;
    if last_char == 'z' or last_char == 'Z':
        google_ts = google_ts[:-1]
    else:
        matches = re.search(r"([-+])(\d\d):(\d\d)$", google_ts)
        if matches is None:
            raise Exception("Cannot parse the timestamp" + google_ts)
        else:
            hour_offset = int(matches.group(2))
            minute_offset = int(matches.group(3))
            operator = matches.group(1)
            tz_offset = minute_offset + hour_offset * 60
            if operator == '+':
                tz_offset = -tz_offset
            google_ts = re.sub('[\-+]\d\d:\d\d$', '', google_ts)
    datetime_obj = datetime.strptime(google_ts, '%Y-%m-%dT%H:%M:%S')
    datetime_obj = datetime_obj + timedelta(minutes=tz_offset)
    utc_datetime = datetime_obj.replace(tzinfo = utc)
    localized_datetime = utc_datetime.astimezone(timezone(LOS_ANGELES_TZ))
    return localized_datetime.replace(tzinfo = None)

def get_phone_number(interviews_list, index):
    return interviews_list[index].phone_number_to_use if index < len(interviews_list) else None

def get_resource_id_for_interviewer(interviewer):
    if interviewer is None:
        return None
    return CFG.get_instance().get("installation", "env_name") + "_" + re.sub("@.*", "", interviewer.email)

class Google_Calendar(object):
    instance = None

    @staticmethod
    def get_calendar():
        if Google_Calendar.instance is None:
            logging.getLogger().setLevel('ERROR')

            CLIENT_SECRETS = os.path.join(os.path.dirname(__file__), '../lib/gcal_sdk/client_secrets.json')
            MISSING_CLIENT_SECRETS_MESSAGE = """ 
WARNING: Please configure OAuth 2.0 for Google Calendar

This cronjob expects Google Calendar client secrets at

%s
    
""" % CLIENT_SECRETS
            FLOW = flow_from_clientsecrets(CLIENT_SECRETS, scope=[
                'https://www.googleapis.com/auth/calendar.readonly',
            ], message=MISSING_CLIENT_SECRETS_MESSAGE)
    
            auth_credentials_path = os.path.join(os.path.dirname(__file__), '../lib/gcal_sdk/auth_credentials.dat')
            storage = Storage(auth_credentials_path)
            credentials = storage.get()
    
            if credentials is None or credentials.invalid:
                credentials = run(FLOW, storage)
    
            calendar = Google_Calendar()

            http = httplib2.Http()
            http = credentials.authorize(http)
            calendar.http = http
    
            calendar.service = build('calendar', 'v3', http=http)
            Google_Calendar.instance = calendar
        return Google_Calendar.instance


    def register_for_push_notifications(self, interviewer):
        hostname = CFG.get_instance().get('installation', 'hostname')
        response = self.service.events().watch(calendarId = interviewer.email, body = {
            'id' : get_resource_id_for_interviewer(interviewer),
            'type' : "web_hook",
            'address' : 'https://' + hostname + '/api/calendar_notification',
            'params' : {
                'ttl' : 24*60*60,
            }
        }).execute()
        interviewer.push_notification_id = response.get("resourceId", "")
        db_session = DB_Session_Factory.get_db_session()
        db_session.add(interviewer)
        db_session.commit()

    def stop_push_notifications(self, interviewer):
        if interviewer.push_notification_id is not None and interviewer.push_notification_id != "": 
            print "Stopping notifications for " + get_resource_id_for_interviewer(interviewer) + ":" + interviewer.push_notification_id;
            try:
                self.service.channels().stop(body = {
                    'id' : get_resource_id_for_interviewer(interviewer),
                    'resourceId' : interviewer.push_notification_id
                }).execute()
            except HttpError, e:
                if e.resp.status in [404]:
                    print "Nothing to stop"
                else:
                    raise e

    def refresh_interviews(self, interviewer, period_start, period_end):
        db_session = DB_Session_Factory.get_db_session()
        db_session.autoflush = False
        try:
            existing_interviews = []
            interviews_to_delete = []
            interviews_for_interviewer = []
            current_date = period_start.date()
            candidate_cache = {}
            existing_interviews = interviewer.interviews.filter(Interview.start_time >= period_start, Interview.start_time < (current_date + timedelta(days=1))).with_lockmode('update').all()
            for existing_interview in existing_interviews:
                interviews_to_delete.append(existing_interview)
            events_request = self.service.events().list(calendarId = interviewer.email, timeZone = LOS_ANGELES_TZ, timeMin = period_start.isoformat(), timeMax = period_end.isoformat(), orderBy = 'startTime', singleEvents = True)
            while (events_request != None):
                response = events_request.execute(self.http)
                for event in response.get('items', []):
                    summary = event.get('summary', '')
                    match = re.search("Interview scheduled for ([\w '.)(]+), (.*?) candidate", summary)
                    if match:
                        if (re.match("^.*?[Ss][Hh][Aa][Dd][Oo][Ww].*?Interview", summary)):
                            continue
                        print "Found interview: " + summary
                        candidate_name = match.group(1)
                        position = match.group(2)
                        candidate = candidate_cache.get(candidate_name, db_session.query(Candidate).get(candidate_name))
                        if candidate is None:
                            candidate = Candidate(candidate_name, position, 'tomas@box.com')
                            candidate_cache[candidate_name] = candidate
                        room = event.get('location', 'Unknown Location')
                        start_time = google_ts_to_datetime(event.get('start', {}).get('dateTime', DEFAULT_DATE))
                        if start_time.date() != current_date:
                            flush_interviews(interviewer, interviews_to_delete, interviews_for_interviewer, current_date, start_time, db_session)
                            current_date = start_time.date()
                            existing_interviews = interviewer.interviews.filter(Interview.start_time >= start_time, Interview.start_time < (current_date + timedelta(days=1))).all()
                            interviews_to_delete = []
                            interviews_for_interviewer = []
                            for existing_interview in existing_interviews:
                                interviews_to_delete.append(existing_interview)

                        end_time = google_ts_to_datetime(event.get('end', {}).get('dateTime', DEFAULT_DATE))
                        interview_exists = False
                        for existing_interview in existing_interviews:
                            if existing_interview.candidate_name == candidate_name:
                                existing_interview.room = room
                                existing_interview.start_time = start_time
                                existing_interview.end_time = end_time
                                existing_interview.candidate = candidate
                                if existing_interview in interviews_to_delete:
                                    interviews_to_delete.remove(existing_interview)
                                interview_exists = True
                                interviews_for_interviewer.append(existing_interview)
                                break
                        if interview_exists is False:
                            new_interview = Interview(interviewer.email, start_time, end_time, candidate_name, room)
                            new_interview.candidate = candidate
                            db_session.add(new_interview)
                            existing_interviews.append(new_interview)
                            interviews_for_interviewer.append(new_interview)
                events_request = self.service.events().list_next(events_request, response)
        except AccessTokenRefreshError:
            print ("The credentials have been revoked or expired, please re-run"
                "the application to re-authorize")
        flush_interviews(interviewer, interviews_to_delete, interviews_for_interviewer, current_date, period_end, db_session)
