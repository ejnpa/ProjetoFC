from sqlalchemy import Column, String, Integer
from database import Base

class Notes(Base):
    __tablename__ = "notes"
    id = Column(String, primary_key=True, index=True)
    title = Column(String, index=True)
    school = Column(String, index=True)
    course = Column(String, index=True)
    year = Column(String, index=True)  
    subject = Column(String, index=True)
    autor = Column(String)
    file_url = Column(String, nullable=True)
    thumbnail_url=Column(String, nullable=True)
    
    
class Users (Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, nullable=False)
    email = Column(String, index=True, nullable=False)
    password = Column(String, nullable=False)
    