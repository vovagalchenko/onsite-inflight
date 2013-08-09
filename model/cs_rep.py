from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, UniqueConstraint, func
from sqlalchemy.orm import relationship, backref
from sqlalchemy.dialects.mysql import BIT, TEXT, VARBINARY
from db_session import DB_Session_Factory
from datetime import datetime, timedelta
from base import Base
import interview

class CS_Rep(Base):
    __tablename__ = 'cs_rep'

    email = Column(String(50), nullable = False, primary_key = True)
    name = Column(String(50), nullable = True)

    def __init__(self, email, name):
        self.email = email
        self.name = name
