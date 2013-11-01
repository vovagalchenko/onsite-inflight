from base import Base
from datetime import datetime, timedelta
from sqlalchemy import Column, String
from sqlalchemy.dialects import mysql
from db_session import DB_Session_Factory
import sys
import hashlib

class User(Base):
    __tablename__ = 'user'

    email = Column(String(50), nullable = False, primary_key = True)
    session_expiration = Column(mysql.TIMESTAMP, nullable = False)
    session_id = Column(mysql.VARBINARY(20), nullable = True)
    # admin_permissions is a bitmask representing permissions the user has to various resources.
    # see the admin_permissions.py file for bit definitions
    admin_permissions = Column(mysql.INTEGER, nullable = False, default = 0)

    def __init__(self, email, session_expiration = (datetime.now() + timedelta(hours = 2))):
        self.email = email
        self.session_expiration = session_expiration
        self.session_id = hashlib.sha1(email + session_expiration.isoformat()).hexdigest()

    @staticmethod
    def user_for_session_cookie(session_id):
        db_session = DB_Session_Factory.get_db_session()
        user = db_session.query(User).filter(User.session_id == session_id).first()
        session_is_active = False
        if user is None or user.session_expiration < datetime.now():
            user = None
        return user

    @staticmethod
    def refresh_user_session(email):
        db_session = DB_Session_Factory.get_db_session()
        user = db_session.query(User).get(email)
        if user is None:
            user = User(email)
        else:
            user.session_expiration = datetime.now() + timedelta(hours = 2)
        db_session.add(user)
        db_session.commit()
        return user
