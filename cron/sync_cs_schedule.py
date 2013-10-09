#!/usr/bin/env python

import sys
import pprint
from model.cs_rep import CS_Rep
from pytz import timezone, utc
from datetime import datetime, timedelta
from lib.calendar import Google_Calendar, google_ts_to_datetime, DEFAULT_DATE, LOS_ANGELES_TZ
from lib.conf import CFG
from model.db_session import DB_Session_Factory
from json import dumps, loads
from oauth2client.client import AccessTokenRefreshError
from apiclient.errors import HttpError
from pytz import timezone
import pdb
import re

target_weekday = 3 # Thursday
target_timerange = [12, 14]
target_calendar_id = "box.com_2av1o7sjlgckgjjmrd032gbtq4@group.calendar.google.com"

def get_ts_from_event(event, ts_key):
    return google_ts_to_datetime(event.get(ts_key, {}).get('dateTime', DEFAULT_DATE))


def main(argv):
    calendar = Google_Calendar.get_calendar()
    db_session = DB_Session_Factory.get_db_session()
    
    now = datetime.now()
    today_weekday = now.weekday()
    next_target_weekday = now + timedelta(days = (target_weekday - today_weekday + 6)%7 + 1)
    la_timezone = timezone(LOS_ANGELES_TZ)
    start_period_naive = datetime(next_target_weekday.year, next_target_weekday.month, next_target_weekday.day, target_timerange[0])
    start_period = la_timezone.localize(start_period_naive)
    end_period_naive = datetime(next_target_weekday.year, next_target_weekday.month, next_target_weekday.day, target_timerange[1])
    end_period = la_timezone.localize(end_period_naive)

    print str(start_period) + " - " + str(end_period)


    try:
        cs_rep_list = db_session.query(CS_Rep).order_by(CS_Rep.email)
        source_events = {}
        for cs_rep in cs_rep_list:
            current_period_start = start_period_naive
            current_period_end = start_period_naive + timedelta(hours = 1)
            print "Checking calendar for " + cs_rep.name
            source_events_request = calendar.service.events().list(calendarId = cs_rep.email, timeZone = LOS_ANGELES_TZ, timeMin = start_period.isoformat(), timeMax = end_period.isoformat(), orderBy = 'startTime', singleEvents = True, maxAttendees = 1000)
            while (source_events_request != None):
                response = source_events_request.execute(calendar.http)
                for event in response.get('items', []):
                    summary = event.get('summary', '')
                    start_time = get_ts_from_event(event, 'start')
                    end_time = get_ts_from_event(event, 'end')
                    if start_time < start_period_naive or end_time > end_period_naive or start_time < current_period_start or end_time - start_time > timedelta(hours=1):
                        continue
                    while current_period_end < end_time:
                        current_period_start = current_period_start + timedelta(hours = 1)
                        current_period_end = current_period_end + timedelta(hours = 1)
                    match = re.search("\*$", summary)
                    if match:
                        source_events[event['id']] = event
                        current_period_start = current_period_start + timedelta(hours = 1)
                        current_period_end = current_period_end + timedelta(hours = 1)
                    else:
                        print "no match: " + summary
                            

                source_events_request = calendar.service.events().list_next(source_events_request, response)

        to_delete = []
        to_update = {}
        target_events_request = calendar.service.events().list(calendarId = target_calendar_id, timeZone = LOS_ANGELES_TZ, timeMin = start_period.isoformat(), timeMax = end_period.isoformat(), orderBy = 'startTime', singleEvents = True)
        while (target_events_request != None):
            response = target_events_request.execute(calendar.http)
            for event in response.get('items', []):
                source_event = source_events.get(event['id'], None)
                if source_event is None:
                    to_delete.append(event)
                else:
                    to_update[event['id']] = {'before' : event, 'after' : source_events[event['id']].copy()}
                    del source_events[event['id']]
            target_events_request = calendar.service.events().list_next(target_events_request, response)

        for event in to_delete:
            print "Removing: " + event.get('summary', "")
            calendar.service.events().delete(calendarId = target_calendar_id, eventId = event['id']).execute(calendar.http)
        for event_id in to_update:
            original_event = to_update[event_id]['before']
            original_start = get_ts_from_event(original_event, 'start')
            original_end = get_ts_from_event(original_event, 'end')
            after_event = to_update[event_id]['after']
            after_start = get_ts_from_event(after_event, 'start')
            after_end = get_ts_from_event(after_event, 'end')
            if original_start != after_start or original_end != after_end:
                original_event['start'] = after_event['start']
                original_event['end'] = after_event['end']
                print "Updating: " + original_event.get('summary', "")
                calendar.service.events().update(calendarId = target_calendar_id, eventId = event_id, body = original_event).execute(calendar.http)
            
        for event_id in source_events:
            source_event = source_events[event_id]
            print "Adding: " + source_event.get('summary', "")
            source_event['organizer'] = {'self' : True}
            source_event['location'] = '4440-3-4 The Marina'
            while True:
                try:
                    calendar.service.events().import_(calendarId = target_calendar_id, body = source_event).execute(calendar.http)
                    break
                except HttpError as e:
                    error_data = loads(e.content)
                    print error_data['error']['code']
                    if error_data.get('error', {'code' : None}).get('code', None) == 400:
                        source_event['sequence'] += 1
                    else:
                        sys.stderr.write("HTTP Error: " + e.content)
                        exit(1)
                    
            
        
    except AccessTokenRefreshError:
        print ("The credentials have been revoked or expired, please re-run"
            "the application to re-authorize")

if __name__ == '__main__':
    main(sys.argv)
