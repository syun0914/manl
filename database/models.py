from sqlalchemy import Column, DateTime, ForeignKey, Integer, Text

from database.session import Base
from sqlalchemy.orm import relationship

class User(Base):
    __tablename__ = 'users'
    
    user_key: str = Column(Text)
    name: str = Column(Text)
    student_id: str = Column(Text)
    level: int = Column(Integer)
    phone: str = Column(Text)
    user_code: int = Column(Integer, primary_key=True, autoincrement=True)


class Admin(Base):
    __tablename__ = 'admins'
    
    user_key: str = Column(Text)
    name: str = Column(Text)
    student_id: str = Column(Text)
    level: int = Column(Integer)
    phone: str = Column(Text)
    admin_code: int = Column(Integer, primary_key=True, autoincrement=True)

    
class Notice(Base):
    __tablename__ = 'notice'
    
    notice_code: int = Column(Integer, primary_key=True, autoincrement=True)
    datetime: DateTime = Column(DateTime)
    title: str = Column(Text)
    content: str = Column(Text)


class NumberBaseball(Base):
    __tablename__ = 'num_baseball'
    
    num_baseball_code: int = Column(Integer, primary_key=True, autoincrement=True)
    user_code: int = Column(Integer, ForeignKey('users.user_code'))
    answer: str = Column(Text(4))
    count: int = Column(Integer)
    datetime: DateTime = Column(DateTime)
    
    user = relationship('User')