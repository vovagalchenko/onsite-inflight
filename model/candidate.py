from base import Base
from sqlalchemy import Column, Integer, String, UniqueConstraint, func, ForeignKey
from sqlalchemy.orm import relationship, backref
from department import Department
import json
from datetime import datetime
from string import split

class Candidate(Base):
    __tablename__ = 'candidate'

    candidate_name = Column(String(50), primary_key = True)
    position = Column(String(100), nullable = False)
    hiring_manager = Column(String(50), ForeignKey('interviewer.email'))
    department_id = Column(Integer, ForeignKey('department.id'))
    interviews = relationship("Interview", backref = backref('candidate'), order_by = 'Interview.end_time', cascade = 'all, delete-orphan');
    department = relationship("Department", backref = backref('candidates'))

    def __init__(self, candidate_name, position, hiring_manager):
        self.candidate_name = candidate_name
        self.position = position
        self.hiring_manager = hiring_manager
        self.department_id = 0
        department = self.calculate_department()
        if department is not None:
            self.department_id = department.id

    def __repr__(self):
        return "<Candidate<'%s'>>" % self.candidate_name

    def calculate_department(self):
        department = None
        for position_token in split(self.position, '/'):
            department = Department.department_for_keyword(position_token.lower())
            if department is not None:
                break
        return department

    def json_representation(self, moment_of_interest = None, show_scores = False):
        interviews_array = []
        if moment_of_interest is None:
            moment_of_interest = datetime.today()
        for interview in self.interviews:
            if interview.end_time.date() == moment_of_interest.date():
                interviews_array.append(interview.dict_representation(show_scores))
        candidate_dict = {
            'candidate_name' : self.candidate_name,
            'position' : self.position,
            'hiring_manager' : self.hiring_manager,
            'interviews' : interviews_array,
        }
        return json.dumps(candidate_dict)
