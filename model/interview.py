from candidate import Candidate
from sqlalchemy import ForeignKey, Column, Integer, String
from sqlalchemy.orm import relationship, backref
from sqlalchemy.dialects import mysql
from sqlalchemy.schema import FetchedValue
from base import Base
import json
import datetime
import calendar

class Interview(Base):
    __tablename__ = 'interview'

    id = Column(Integer, primary_key = True)
    interviewer_email = Column(String(50), ForeignKey('interviewer.email'))
    start_time = Column(mysql.TIMESTAMP, nullable = False)
    end_time = Column(mysql.TIMESTAMP, nullable = False)
    candidate_name = Column(String(50), ForeignKey('candidate.candidate_name'), nullable = False)
    phone_number_to_use = Column(String(10), nullable = False)
    room = Column(String(50), nullable = False)
    technical_score = Column(mysql.FLOAT(), nullable = True)
    cultural_score = Column(mysql.FLOAT(), nullable = True)
    notes = Column(mysql.TEXT, nullable = True)
    number_of_pings = Column(mysql.TINYINT, nullable = False, default = 0)
    hire = Column(mysql.TINYINT, nullable = False, default = -1)
    # The following timestamp columns are only updated by triggers. They are effectively readonly for the model code.
    # An update to these columns will be caught by a MySQL trigger and will not be performed.
    technical_score_ts = Column(mysql.TIMESTAMP, server_default = FetchedValue(), server_onupdate = FetchedValue(for_update=True))
    cultural_score_ts = Column(mysql.TIMESTAMP, server_default = FetchedValue(), server_onupdate = FetchedValue(for_update=True))
    notes_ts = Column(mysql.TIMESTAMP, server_default = FetchedValue(), server_onupdate = FetchedValue(for_update=True))

    def __init__(self, email, start_time, end_time, candidate_name, room):
        self.interviewer_email = email
        self.start_time = start_time
        self.end_time = end_time
        self.candidate_name = candidate_name
        self.room = room
        self.number_of_pings = 0
        self.hire = -1

    def __repr__(self):
        return "<Interview<'%s'>" % self.candidate_name

    def is_coffee_break(self):
        return (self.end_time - self.start_time).total_seconds() <= self.candidate.department.maximum_coffee_break_length;

    @staticmethod
    def datetime_to_string(ts):
        if ts is None:
            return None
        dtnow = datetime.datetime.now()
        dtutcnow = datetime.datetime.utcnow()
        delta = dtnow - dtutcnow
        hh,mm = divmod((delta.days * 24*60*60 + delta.seconds + 30) // 60, 60)
        return "%s%+03d:%02d" % (ts.isoformat(), hh, mm)

    def dict_representation(self, show_scores = False):
        interviewer = self.interviewer.dict_representation()
        if self.interviewer.avatar_url is not None:
            interviewer['avatar_url'] = self.interviewer.avatar_url
        interview_dict = {
            'id' : self.id,
            'interviewer' : interviewer,
            'start_time' : Interview.datetime_to_string(self.start_time),
            'end_time' : Interview.datetime_to_string(self.end_time),
            'candidate_name' : self.candidate_name,
            'room' : self.room,
            'number_of_pings' : self.number_of_pings,
            'is_coffee_break' : self.is_coffee_break(),
            'technical_score_ts' : Interview.datetime_to_string(self.technical_score_ts),
            'cultural_score_ts' : Interview.datetime_to_string(self.cultural_score_ts),
            'notes_ts' : Interview.datetime_to_string(self.notes_ts)
        }
        if show_scores is True:
            interview_dict['technical_score'] = self.technical_score
            interview_dict['cultural_score'] = self.cultural_score
            interview_dict['hire'] = self.hire
            interview_dict['notes'] = self.notes
        return interview_dict
