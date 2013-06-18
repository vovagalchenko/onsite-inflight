from interviewer import *
from sqlalchemy import Enum
from sqlalchemy.dialects import mysql
import json

class Log(Base):
    __tablename__ = 'log'
    
    id = Column(Integer, primary_key = True)
    time = Column(mysql.TIMESTAMP, nullable = False)
    event_name = Column(Enum('INCOMING_SMS', 'OUTGOING_SMS'), nullable = False)
    phone_number = Column(String(10), nullable = True)
    data = Column(mysql.MEDIUMTEXT, nullable = True)

    def __init__(self, event_name, phone_number, data):
        self.event_name = event_name
        self.phone_number = phone_number
        self.data = json.dumps(data)
