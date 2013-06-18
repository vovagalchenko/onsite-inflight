from base import Base
from datetime import datetime, timedelta
from sqlalchemy import Column, String
from sqlalchemy.dialects import mysql
from db_session import DB_Session_Factory
import hashlib

class User(Base):
    __tablename__ = 'user'

    email = Column(String(50), nullable = False, primary_key = True)
    session_expiration = Column(mysql.TIMESTAMP, nullable = False)
    session_id = Column(mysql.VARBINARY(20), nullable = True)

    def __init__(self, email, session_expiration = (datetime.now() + timedelta(hours = 2))):
        self.email = email
        self.session_expiration = session_expiration
        self.session_id = hashlib.sha1(email + session_expiration.isoformat()).hexdigest()

    @staticmethod
    def session_is_active(session_id):
        db_session = DB_Session_Factory.get_db_session()
        user = db_session.query(User).filter(User.session_id == session_id).first()
        session_is_active = False
        if user is not None and user.session_expiration > datetime.now():
            session_is_active = True
        return session_is_active

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
