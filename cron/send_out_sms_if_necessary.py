#!/usr/bin/env python

from model.db_session import DB_Session_Factory
from model.interview import Interview
from datetime import datetime
from lib.send_sms import send_initial_request_for_scores
import sys

MAX_NUMBER_OF_PINGS = 3

db_session = DB_Session_Factory.get_db_session()
for interview in db_session.query(Interview).from_statement('select i.* from interview i join (select max(end_time) lastint, interviewer_email from interview where end_time < :latest_end_time and date(start_time) = date(now()) group by interviewer_email, phone_number_to_use) l  where i.interviewer_email=l.interviewer_email and i.end_time=l.lastint').params(latest_end_time = datetime.now()).all():
    if interview.technical_score is None and interview.cultural_score is None and interview.number_of_pings < MAX_NUMBER_OF_PINGS:
        try:
            send_initial_request_for_scores(interview)
        except:
            e = sys.exc_info()[0]
            sys.stderr.write("Exception caught while trying to send SMS for interview <%d>: %s" % (interview.id, e.strerror))
        else:
            interview.number_of_pings += 1
            db_session.commit()
