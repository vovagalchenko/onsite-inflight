from sqlalchemy import *
from sqlalchemy.orm import sessionmaker

class DB_Session_Factory(object):
    session = None

    @staticmethod
    def get_db_session():
        if DB_Session_Factory.session is None:
            db_engine = create_engine('mysql://root@localhost:3838/onsite_inflight?unix_socket=/var/onsite-inflight/data/mysql/tmp/mysql.sock', echo=False)
            Session = sessionmaker(bind = db_engine)
            DB_Session_Factory.session = Session()
        return DB_Session_Factory.session
