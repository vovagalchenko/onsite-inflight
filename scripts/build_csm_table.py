#!/usr/bin/env python

import sys
from model.db_session import DB_Session_Factory
from model.cs_rep import CS_Rep
import re

def main(argv):
    db_session = DB_Session_Factory.get_db_session()
    deletion_sql = CS_Rep.__table__.delete('1')
    db_session.execute(deletion_sql)
    interviewers = {}
    
    with open("../data/bootstrap/cs_reps.dat", "r") as csm_rep_file:
        for csm_rep_info in csm_rep_file:
            csm_rep_info = csm_rep_info.strip(' \t\n\r')
            if not csm_rep_info:
                continue
            csm_rep_data = csm_rep_info.split("\t")
            print csm_rep_data[0] + "\t" + csm_rep_data[1]
            csm_rep = CS_Rep(csm_rep_data[1], csm_rep_data[0])
            db_session.add(csm_rep)
    db_session.commit()
    print "Done"

if __name__ == '__main__':
    main(sys.argv)
