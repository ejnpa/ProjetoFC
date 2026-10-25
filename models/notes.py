from sqlalchemy import Column, String, Integer
from sqlalchemy.orm import relationship
from database import Base

class Notes(Base):
    __tablename__ = "notes"
    id = Column(String, primary_key=True, index=True)
    title = Column(String, index=True)
    school = Column(String, index=True)
    course = Column(String, index=True)
    year = Column(String, index=True)  
    subject = Column(String, index=True)
    author = Column(String)
    file_url = Column(String, nullable=True)
    thumbnail_url=Column(String, nullable=True)
    
    like_list = relationship("NoteLike", lazy = "joined")
    