from db_session import DB_Session_Factory
from base import Base
from sqlalchemy import ForeignKey, Column, Integer, String, func
from sqlalchemy.orm import relationship
from sqlalchemy.dialects import mysql
from sqlalchemy.schema import FetchedValue
import json
import datetime

class Department(Base):
    __tablename__ = 'department'

    id = Column(Integer, primary_key = True)
    name = Column(String(50), nullable = False)
    maximum_coffee_break_length = Column(mysql.SMALLINT(), nullable = False, default=900) # in seconds
    recruiter_name = Column(String(50), nullable = False)
    recruiter_email = Column(mysql.VARBINARY(50), nullable = False)
    recruiter_phone_number = Column(mysql.CHAR(10), nullable = False)

    def __init__(self, id, name, maximum_coffee_break_length, recruiter_name, recruiter_email, recruiter_phone_number):
        self.id = id
        self.name = name
        self.maximum_coffee_break_length = maximum_coffee_break_length
        self.recruiter_name = recruiter_name
        self.recruiter_email = recruiter_email
        self.recruiter_phone_number = recruiter_phone_number

    @staticmethod
    def department_for_keyword(keyword):
        db_session = DB_Session_Factory.get_db_session()
        best_dep_keyword = None
        for dep_keyword in db_session.query(Department_Keyword).filter(func.instr(keyword, Department_Keyword.keyword) > 0):
            if best_dep_keyword is None or len(best_dep_keyword.keyword) < len(dep_keyword.keyword):
                best_dep_keyword = dep_keyword
        department = None
        if best_dep_keyword is not None:
            department = db_session.query(Department).get(best_dep_keyword.department_id)
        return department

class Department_Keyword(Base):
    __tablename__ = 'department_keyword'

    id = Column(Integer, primary_key = True)
    department_id = Column(Integer, nullable = False)
    keyword = Column(String(100), nullable = False)

    def __init__(self, department_id, keyword):
        self.department_id = department_id
        self.keyword = keyword
