#!/usr/bin/env python

import sys
from model.db_session import DB_Session_Factory
from model.interview import Interview
from model.interviewer import Interviewer
from model.optin import Opt_In
from urllib import urlretrieve
from os import listdir, remove, path
from lib.conf import CFG
import re

ROOT = CFG.get_instance().get('installation', 'root') + '/code/webapp'

def main(argv):
    db_session = DB_Session_Factory.get_db_session()
    deletion_sql = Interviewer.__table__.delete('1')
    db_session.execute(deletion_sql)
    interviewers = {}
    
    with open("scripts/interviewers.dat", "r") as interviewer_file:
        for interviewer_info in interviewer_file:
            interviewer_info = interviewer_info.strip(' \t\n\r')
            if not interviewer_info:
                continue
            interviewer_data = interviewer_info.split("\t")
            print interviewer_data[0] + "\t" + interviewer_data[1] + "\t" + interviewer_data[2]
            interviewer = Interviewer(interviewer_data[1], interviewer_data[0], interviewer_data[2])
            if len(interviewer_data) == 4:
                original_url = interviewer_data[3]
                final_url = '/avatars/' + interviewer.name.lower().replace(' ', '-')
                match = re.search('\.([^.]*?)$', original_url)
                if match:
                    final_url += '.' + match.group(1)
                local_path = ROOT + final_url
                if not path.isfile(local_path):
                    print 'Downloading image for ' + final_url
                    urlretrieve(interviewer_data[3], local_path)
                interviewer.avatar_url = final_url
            interviewers[interviewer_data[1]] = interviewer
            db_session.add(interviewer)

    print "Adding opt-ins now..."
    for optin in db_session.query(Opt_In):
        if interviewers.get(optin.email, None) is None:
            print optin.name + "\t" + optin.email + "\t" + optin.phone_number;
            db_session.add(Interviewer(optin.email, optin.name, optin.phone_number))
    db_session.commit()

if __name__ == '__main__':
    main(sys.argv)
