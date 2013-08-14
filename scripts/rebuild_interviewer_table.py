#!/usr/bin/env python

import sys
from model.db_session import DB_Session_Factory
from model.interview import Interview
from model.interviewer import Interviewer
from model.interviewer_tag import Interviewer_Tag
from urllib import urlretrieve
from os import listdir, remove, path, walk
from lib.conf import CFG
import re

ROOT = CFG.get_instance().get('installation', 'root') + '/code/webapp'

def main(argv):
    db_session = DB_Session_Factory.get_db_session()
    deletion_sql = Interviewer.__table__.delete('1')
    db_session.execute(deletion_sql)
    interviewers = {}
    
    with open("../data/bootstrap/interviewers.dat", "r") as interviewer_file:
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

    db_session.execute(Interviewer_Tag.__table__.delete('1'))

    for dir_name, dir_names, file_names in walk("../data/bootstrap/tags", "r"):
        for tag_name in file_names:
            print "Adding tag <" + tag_name + ">"
            file_path = path.join(dir_name, tag_name)
            tag = Interviewer_Tag(tag_name)
            interviewers_for_tag = []
            with open(file_path, "r") as tag_file:
                for interviewer_email in tag_file:
                    interviewer_email = interviewer_email.strip(' \t\n\r')
                    interviewer = db_session.query(Interviewer).get(interviewer_email)
                    if interviewer is None:
                        raise Exception("Invalid interviewer info in the bootstrap data: " + interviewer_email)
                    tag.add_interviewer(interviewer)
            db_session.add(tag)
    db_session.commit()

if __name__ == '__main__':
    main(sys.argv)
