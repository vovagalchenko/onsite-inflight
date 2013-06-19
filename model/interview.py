from interviewer import *
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship, backref
from sqlalchemy.dialects import mysql
import json
import datetime
import calendar
import candidate

class Interview(Base):
    __tablename__ = 'interview'

    id = Column(Integer, primary_key = True)
    interviewer_email = Column(String(50), ForeignKey('interviewer.email'))
    start_time = Column(mysql.TIMESTAMP, nullable = False)
    end_time = Column(mysql.TIMESTAMP, nullable = False)
    candidate_name = Column(String(50), ForeignKey('candidate.candidate_name'), nullable = False)
    room = Column(String(50), nullable = False)
    technical_score = Column(mysql.FLOAT(), nullable = True)
    cultural_score = Column(mysql.FLOAT(), nullable = True)
    number_of_pings = Column(mysql.TINYINT, nullable = False, default = 0)

    def __init__(self, email, start_time, end_time, candidate_name, room):
        self.interviewer_email = email
        self.start_time = start_time
        self.end_time = end_time
        self.candidate_name = candidate_name
        self.room = room
        self.number_of_pings = 0

    def __repr__(self):
        return "<Interview<'%s'>" % self.candidate_name

    def is_coffee_break(self):
        return (self.end_time - self.start_time).total_seconds() <= 30*60;

    @staticmethod
    def datetime_to_string(ts):
        dtnow = datetime.datetime.now()
        dtutcnow = datetime.datetime.utcnow()
        delta = dtnow - dtutcnow
        hh,mm = divmod((delta.days * 24*60*60 + delta.seconds + 30) // 60, 60)
        return "%s%+03d:%02d" % (ts.isoformat(), hh, mm)

    def dict_representation(self):
        return {
            'id' : self.id,
            'interviewer' :
            {
                'name' : self.interviewer.name,
                'email' : self.interviewer.email,
                'phone_number' : self.interviewer.phone_number,
                'avatar_url' : self.interviewer.avatar_url,
            },
            'start_time' : Interview.datetime_to_string(self.start_time),
            'end_time' : Interview.datetime_to_string(self.end_time),
            'candidate_name' : self.candidate_name,
            'room' : self.room,
            'technical_score' : self.technical_score,
            'cultural_score' : self.cultural_score,
            'number_of_pings' : self.number_of_pings,
            'is_coffee_break' : self.is_coffee_break(),
        };