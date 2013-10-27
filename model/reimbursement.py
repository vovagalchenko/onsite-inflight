from base import *
from sqlalchemy import Column
from sqlalchemy.dialects import mysql

class Reimbursement(Base):
    __tablename__ = 'reimbursement'
    
    id = Column(mysql.VARBINARY(50), primary_key = True, nullable = False)
    max_amount = Column(mysql.INTEGER(10), nullable = False, default = 0)
    details = Column(mysql.VARBINARY(1000), nullable = False, default = "")
    name = Column(mysql.VARBINARY(100), nullable = False, default = "")

    def __init__(self, id, name, max_amount, details):
        self.id = id
        self.name = name
        self.max_amount = max_amount
        self.detials = details

    def dict_representation(self):
        return {
            'id' : self.id,
            'name' : self.name,
            'max_amount' : self.max_amount,
            'details' : self.details
        }
