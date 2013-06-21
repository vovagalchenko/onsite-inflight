#!/usr/bin/env python

from db_session import DB_Session_Factory
from log_event import Log

def log(event_name, phone_number, data):
    if len(phone_number) > 10:
        phone_number = phone_number[2:]
    db_session = DB_Session_Factory.get_db_session()
    log_event = Log(event_name, phone_number, data)
    db_session.add(log_event)
    db_session.commit()

def log_incoming_sms(phone_number, data):
    log('INCOMING_SMS', phone_number, data)

def log_outgoing_sms(phone_number, data):
    log('OUTGOING_SMS', phone_number, data)
