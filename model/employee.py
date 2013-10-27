from base import *
from sqlalchemy import Column
from sqlalchemy.dialects import mysql

class Employee(Base):
    __tablename__ = 'employee'
    
    email = Column(mysql.VARBINARY(50), primary_key = True, nullable = False)
    gym = Column(mysql.INTEGER(10), nullable = False, default = 0)
    mobile = Column(mysql.INTEGER(10), nullable = False, default = 0)

    def __init__(self, email):
        self.email = email
        self.gym = 0
        self.mobile = 0

    def dict_representation(self):
        return {
            'email' : self.email,
            'gym' : self.gym,
            'mobile' : self.mobile
        }
