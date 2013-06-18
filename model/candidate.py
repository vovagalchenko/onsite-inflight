from interview import *
import json
from datetime import datetime

class Candidate(Base):
    __tablename__ = 'candidate'

    candidate_name = Column(String(50), primary_key = True)
    position = Column(String(50), nullable = False)
    hiring_manager = Column(String(50), ForeignKey('interviewer.email'))
    interviews = relationship("Interview", backref = backref('candidate'), order_by = 'Interview.end_time', cascade = 'all, delete-orphan');

    def __init__(self, candidate_name, position, hiring_manager):
        self.candidate_name = candidate_name
        self.position = position
        self.hiring_manager = hiring_manager

    def __repr__(self):
        return "<Candidate<'%s'>>" % self.candidate_name

    def json_representation(self, moment_of_interest = None):
        interviews_array = []
        if moment_of_interest is None:
            moment_of_interest = datetime.today()
        for interview in self.interviews:
            if interview.end_time.date() == moment_of_interest.date():
                interviews_array.append(interview.dict_representation())
        candidate_dict = {
            'candidate_name' : self.candidate_name,
            'position' : self.position,
            'hiring_manager' : self.hiring_manager,
            'interviews' : interviews_array,
        }
        return json.dumps(candidate_dict)
