from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, UniqueConstraint
from sqlalchemy.dialects import mysql
from db_session import DB_Session_Factory
from datetime import datetime, timedelta
from base import Base

class Opt_In(Base):
    __tablename__ = 'optin'

    email = Column(String(50), nullable = False)
    name = Column(String(50), nullable = True)
    phone_number = Column(String(10), nullable = False, primary_key = True)
    updated = Column(mysql.TIMESTAMP, nullable = False)

    def __init__(self, email, name, phone_number):
        self.email = email
        self.name = name
        self.phone_number = phone_number

    @staticmethod
    def get_opt_ins_after_date(min_date):
        if min_date is None:
            min_date = datetime.fromtimestamp(28800)
        db_session = DB_Session_Factory.get_db_session()
        return db_session.query(Opt_In).filter(Opt_In.updated > min_date).order_by(Opt_In.updated.asc())

    def nickname(self):
        return self.name.split()[0] + " " + self.name.split()[-1][0] + '.'

    def dict_representation(self):
        return {
            'email' : self.email,
            'name' : self.name,
            'phone_number' : self.phone_number,
            'nickname' : self.nickname(),
            'updated' : self.updated.strftime("%s")
        }

    def __repr__(self):
        return "<Interviewer<'%s'>" % self.name
