#!/usr/bin/env python

import sys
from lib.conf import CFG

root_path = CFG.get_instance().get('installation', 'root')
sys.path.insert(1, root_path + "/code/lib/gcal_sdk")

import gflags
import httplib2
import os
import pprint
import re
import logging
from copy import copy
from model.interviewer import Interviewer
from model.interview import Interview
from model.candidate import Candidate
from model.db_session import DB_Session_Factory
from pytz import timezone
from datetime import datetime, timedelta

from apiclient.discovery import build
from oauth2client.file import Storage
from oauth2client.client import AccessTokenRefreshError
from oauth2client.client import flow_from_clientsecrets
from oauth2client.tools import run

SECS_IN_DAY = 24*60*60
LOS_ANGELES_TZ = 'America/Los_Angeles'
FLAGS = gflags.FLAGS
DEFAULT_DATE = '1970-01-01T07:00:00-07:00'

# CLIENT_SECRETS, name of a file containing the OAuth 2.0 information for this
# application, including client_id and client_secret.
# You can see the Client ID and Client secret on the API Access tab on the
# Google APIs Console <https://code.google.com/apis/console>
CLIENT_SECRETS = os.path.join(os.path.dirname(__file__), '../lib/gcal_sdk/client_secrets.json')

# Helpful message to display if the CLIENT_SECRETS file is missing.
MISSING_CLIENT_SECRETS_MESSAGE = """
WARNING: Please configure OAuth 2.0 for Google Calendar

This cronjob expects Google Calendar client secrets at

   %s

""" % CLIENT_SECRETS

# Set up a Flow object to be used for authentication.
# Add one or more of the following scopes. PLEASE ONLY ADD THE SCOPES YOU
# NEED. For more information on using scopes please see
# <https://developers.google.com/+/best-practices>.
FLOW = flow_from_clientsecrets(CLIENT_SECRETS,
    scope=[
      'https://www.googleapis.com/auth/calendar.readonly',
    ],
    message=MISSING_CLIENT_SECRETS_MESSAGE)


# The gflags module makes defining command-line options easy for
# applications. Run this program with the '--help' argument to see
# all the flags that it understands.
gflags.DEFINE_enum('logging_level', 'ERROR',
    ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
    'Set the level of logging detail.')


def main(argv):
  # Let the gflags module process the command-line arguments
  try:
    argv = FLAGS(argv)
  except gflags.FlagsError, e:
    print '%s\\nUsage: %s ARGS\\n%s' % (e, argv[0], FLAGS)
    sys.exit(1)

  # Set the logging according to the command-line flag
  logging.getLogger().setLevel(getattr(logging, FLAGS.logging_level))

  # If the Credentials don't exist or are invalid, run through the native
  # client flow. The Storage object will ensure that if successful the good
  # Credentials will get written back to a file.
  auth_credentials_path = os.path.join(os.path.dirname(__file__), '../lib/gcal_sdk/auth_credentials.dat')
  storage = Storage(auth_credentials_path)
  credentials = storage.get()

  if credentials is None or credentials.invalid:
    credentials = run(FLOW, storage)

  # Create an httplib2.Http object to handle our HTTP requests and authorize it
  # with our good Credentials.
  http = httplib2.Http()
  http = credentials.authorize(http)

  service = build('calendar', 'v3', http=http)

  try:

    now = datetime.now(timezone(LOS_ANGELES_TZ))
    today_start = datetime(year = now.year, month = now.month, day = now.day, tzinfo = now.tzinfo)
#    today_start = today_start - timedelta(days=1)
    tomorrow = today_start + timedelta(days = 1)
    today_end = datetime(year = tomorrow.year, month = tomorrow.month, day = tomorrow.day, tzinfo = tomorrow.tzinfo)
    db_session = DB_Session_Factory.get_db_session()
    for interviewer in db_session.query(Interviewer).order_by(Interviewer.email):
        print "Checking schedule for " + interviewer.name
        existing_interviews = interviewer.todays_interviews
        interviews_to_delete = []
        for existing_interview in existing_interviews:
            interviews_to_delete.append(existing_interview)
        events_request = service.events().list(calendarId = interviewer.email, timeZone = LOS_ANGELES_TZ, timeMin = today_start.isoformat(), timeMax = today_end.isoformat(), orderBy = 'startTime', singleEvents = True)
        while (events_request != None):
            response = events_request.execute(http)
            for event in response.get('items', []):
                summary = event.get('summary', '')
                match = re.search("Interview scheduled for ([\w '.]+), (.*?) candidate", summary)
                if match:
                    if (re.match("^.*?[Ss][Hh][Aa][Dd][Oo][Ww].*?Interview", summary)):
                        continue
                    print "Found interview: " + summary
                    candidate_name = match.group(1)
                    position = match.group(2)
                    candidate = db_session.query(Candidate).get(candidate_name)
                    if candidate is None:
                        candidate = Candidate(candidate_name, position, 'tomas@box.com')
                    room = event.get('location', 'Unknown Location')
                    start_time = google_ts_to_datetime(event.get('start', {}).get('dateTime', DEFAULT_DATE))
                    end_time = google_ts_to_datetime(event.get('end', {}).get('dateTime', DEFAULT_DATE))
                    interview_exists = False
                    for existing_interview in existing_interviews:
                        if existing_interview.candidate_name == candidate_name:
                            existing_interview.room = room
                            existing_interview.start_time = start_time
                            existing_interview.end_time = end_time
                            existing_interview.candidate = candidate
                            interviews_to_delete.remove(existing_interview)
                            interview_exists = True
                            break
                    if interview_exists is False:
                        new_interview = Interview(interviewer.email, start_time, end_time, candidate_name, room)
                        new_interview.candidate = candidate
                        db_session.add(new_interview)
            events_request = service.events().list_next(events_request, response)
        for interview_to_delete in interviews_to_delete:
            print "Deleting interview with " + interview_to_delete.candidate_name
            candidate = interview_to_delete.candidate
            db_session.delete(interview_to_delete)
            if not candidate.interviews:
                db_session.delete(candidate)
        db_session.commit()

    # For more information on the Calendar API API you can visit:
    #
    #   https://developers.google.com/google-apps/calendar/firstapp
    #
    # For more information on the Calendar API API python library surface you
    # can visit:
    #
    #   https://google-api-client-libraries.appspot.com/documentation/calendar/v3/python/latest/
    #
    # For information on the Python Client Library visit:
    #
    #   https://developers.google.com/api-client-library/python/start/get_started

  except AccessTokenRefreshError:
    print ("The credentials have been revoked or expired, please re-run"
      "the application to re-authorize")

def google_ts_to_datetime(google_ts):
    google_ts = re.sub('-\d\d:\d\d$', '', google_ts)
    return datetime.strptime(google_ts, '%Y-%m-%dT%H:%M:%S')
    

if __name__ == '__main__':
  main(sys.argv)
