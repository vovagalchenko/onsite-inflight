#!/usr/bin/env python

import sys
import pprint
from model.interviewer import Interviewer
from pytz import timezone, utc
from datetime import datetime, timedelta
from lib.calendar import Google_Calendar
from lib.conf import CFG
from model.db_session import DB_Session_Factory

LOS_ANGELES_TZ = "America/Los_Angeles"

def main(argv):
    update_dirty_calendars_only = False
    if len(argv) is 2 and argv[1] == "dirty_only":
        update_dirty_calendars_only = True
    now = datetime.now(timezone(LOS_ANGELES_TZ))
    period_start = datetime(year = now.year, month = now.month, day = now.day, tzinfo = now.tzinfo)
    period_end = period_start + timedelta(days = int(CFG.get_instance().get('refresh_interview_schedule', 'num_days_to_get_schedule_for')))
    calendar = Google_Calendar.get_calendar()
    db_session = DB_Session_Factory.get_db_session()
    if update_dirty_calendars_only is True:
        interviewer_list = db_session.query(Interviewer).filter(Interviewer.needs_calendar_sync == 1).with_lockmode('update').all()
        for interviewer in interviewer_list:
            interviewer.needs_calendar_sync = 0
        db_session.commit()
    else:
        interviewer_list = db_session.query(Interviewer).filter(Interviewer.does_interviews == 1).order_by(Interviewer.email)
    for interviewer in interviewer_list:
        print "Checking schedule for " + interviewer.name
        calendar.refresh_interviews(interviewer, period_start, period_end)
        calendar.stop_push_notifications(interviewer)
#        calendar.register_for_push_notifications(interviewer)
        
if __name__ == '__main__':
  main(sys.argv)
