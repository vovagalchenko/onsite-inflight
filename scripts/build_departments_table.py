#!/usr/bin/env python

import sys
from model.db_session import DB_Session_Factory
from model.department import Department, Department_Keyword
from model.interviewer import Interviewer
from model.candidate import Candidate
import json

def main(argv):
    db_session = DB_Session_Factory.get_db_session()
    deletion_sql = Department.__table__.delete('1')
    db_session.execute(deletion_sql)
    deletion_sql = Department_Keyword.__table__.delete('1')
    db_session.execute(deletion_sql)

    f = open("../data/bootstrap/departments.json", 'r')
    departments_string = f.read()
    departments = json.loads(departments_string)
    for department_dict in departments:
        department = Department(department_dict['id'], department_dict['name'], department_dict['maximum_coffee_break_length'], department_dict['recruiter_name'], department_dict['recruiter_email'], department_dict['recruiter_phone_number'])
        db_session.add(department)
        db_session.commit()
        for keyword in department_dict.get('keywords', []):
            department_keyword = Department_Keyword(department.id, keyword)
            db_session.add(department_keyword)
        db_session.commit()
    for candidate in db_session.query(Candidate):
        department = candidate.calculate_department()
        if department is None:
            department_name = "None"
            department_id = 0
        else:
            department_name = department.name
            department_id = department.id
        candidate_position = "None" if candidate.position is None else candidate.position
        print '\t\t'.join([candidate.candidate_name, candidate.position, department_name])
        if candidate.department_id is not None:
            candidate.department_id = department_id
            db_session.add(candidate)
    db_session.commit()
    
if __name__ == '__main__':
    main(sys.argv)
