from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, UniqueConstraint, func
from sqlalchemy.orm import relationship, backref
from sqlalchemy.dialects.mysql import TEXT
from db_session import DB_Session_Factory
from datetime import datetime, timedelta
from base import Base
import interview

class Interviewer_Tag(Base):
    __tablename__ = 'interviewer_tag'

    tag = Column(String(50), nullable = False, primary_key = True)
    interviewer_emails = Column(TEXT, nullable = False, primary_key = False)

    def __init__(self, tag, interviewer_emails = None):
        self.tag = tag
        self.interviewer_emails = interviewer_emails

    def get_interviewers(self):
        ret_val = set([])
        if self.interviewer_emails is not None:
            ret_val = set(self.interviewer_emails.split(","))
        return ret_val

    def add_interviewer(self, interviewer):
        existing_emails = self.get_interviewers()
        existing_emails.update([interviewer.email])
        self.interviewer_emails = ",".join(existing_emails)
