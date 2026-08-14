from sqlalchemy import Column, String, Integer
from database import Base

class Users (Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, nullable=False)
    email = Column(String, index=True, nullable=False)
    password = Column(String, nullable=False)