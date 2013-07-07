#!/usr/bin/env python

import model.db_session
from model.interview import Interview
from model.interviewer import Interviewer
from model.log_event import Log
from model.db_session import DB_Session_Factory
from api.http_response_builder.sms.handle_score_sms import Handle_Score_SMS_HTTP_Response_Builder
from sqlalchemy import func
import json

db_session = DB_Session_Factory.get_db_session()
db_session.connection(None).execute("SET @TRIGGERS_DISABLED = TRUE;")
for interview in db_session.query(Interview).yield_per(5):
    interviewer_phone_number = db_session.query(Interviewer).get(interview.interviewer_email).phone_number
    print ("Looking to fix interview " + str(interview.id))
    print ("Interviewer phone #: " + interviewer_phone_number)
    for log_row in db_session.query(Log).filter(func.date(interview.end_time) == func.date(Log.time), Log.time > interview.end_time, Log.event_name == 'INCOMING_SMS', Log.phone_number == interviewer_phone_number):
        if interview.technical_score is not None and interview.technical_score_ts is None:
            msg_body = json.loads(log_row.data)['Body']
            if isinstance(msg_body, basestring):
                msg_body = [msg_body]
            msg_body = msg_body[0]
            print ("Msg <" + str(log_row.id) + ">: " + msg_body)
            msg_score = Handle_Score_SMS_HTTP_Response_Builder.parse_score(msg_body)
            if msg_score is not None:
                if msg_score != interview.technical_score:
                    raise Exception('Technical scores in the interview and log tables do not match for interview_id ' + str(interview.id) + ". Interview table score: " + str(interview.technical_score) + ". Log table score: " + str(msg_score))
                interview.technical_score_ts = log_row.time
                print "Fixing technical ts for interview_id: " + str(interview.id)
                db_session.commit()
        elif interview.cultural_score is not None and interview.cultural_score_ts is None:
            msg_body = json.loads(log_row.data)['Body']
            if isinstance(msg_body, basestring):
                msg_body = [msg_body]
            msg_body = msg_body[0]
            print ("Msg <" + str(log_row.id) + ">: " + msg_body)
            msg_score = Handle_Score_SMS_HTTP_Response_Builder.parse_score(msg_body)
            if msg_score is not None:
                if msg_score != interview.cultural_score:
                    raise Exception('Cultural scores in the interview and log tables do not match for interview_id ' + str(interview.id) + ". Interview table score: " + str(interview.cultural_score) + ". Log table score: " + str(msg_score))
                interview.cultural_score_ts = log_row.time
                print "Fixing cultural ts for interview_id: " + str(interview.id)
                db_session.commit()
    if interview.technical_score is not None and interview.technical_score != 0 and interview.technical_score_ts is None:
        raise Exception('Unable to come up with the technical score timestamp for interview id: ' + str(interview.id))
    if interview.cultural_score is not None and interview.cultural_score != 0 and interview.cultural_score_ts is None:
        raise Exception('Unable to come up with the cultural score timestamp for interview id: ' + str(interview.id))
