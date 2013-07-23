from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, UniqueConstraint, func
from sqlalchemy.orm import relationship, backref
from db_session import DB_Session_Factory
from datetime import datetime, timedelta
from base import Base
import interview

class Interviewer(Base):
    __tablename__ = 'interviewer'

    email = Column(String(50), nullable = False, primary_key = True)
    name = Column(String(50), nullable = True)
    phone_number = Column(String(10), nullable = False)
    avatar_url = Column(String(2083))
    # The delete-orphan cascade option makes the framework remove the row associated with the interview
    # when it is disassociated from the interviewer. It makes no sense to have an interview with no interviewer.
    interviews = relationship(
        "Interview",
        backref = backref('interviewer'),
        cascade = "all, delete-orphan",
        order_by='Interview.end_time'
    )
    todays_interviews = relationship(
        "Interview",
        cascade = "all, delete-orphan",
        order_by = 'Interview.end_time',
        primaryjoin = "and_(Interviewer.email==Interview.interviewer_email, func.date(Interview.start_time) == func.date(func.now()))"
    )

    UniqueConstraint(phone_number)

    def __init__(self, email, name, phone_number):
        self.email = email
        self.name = name
        self.phone_number = phone_number

    @staticmethod
    def get_interviewer_by_phone_number(phone_number):
        session = DB_Session_Factory.get_db_session()
        return session.query(Interviewer).filter(Interviewer.phone_number == phone_number).first()

    def dict_representation(self):
        return {'name' : self.name, 'avatar_url' : self.avatar_url, 'email' : self.email}

    def get_most_recently_completed_interview(self, phone_number, for_update = False):
        last_interview = None
        db_session = DB_Session_Factory.get_db_session()
        query = db_session.query(interview.Interview).filter(interview.Interview.interviewer_email==self.email, func.date(interview.Interview.start_time) == func.date(func.now()), interview.Interview.end_time < func.now(), interview.Interview.phone_number_to_use == phone_number).order_by(interview.Interview.end_time.desc())
        if for_update is True:
            query = query.with_lockmode('update')
        return query.first()

    def nickname(self):
        return self.name.split()[0]

    def __repr__(self):
        return "<Interviewer<'%s'>" % self.name
