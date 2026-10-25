from sqlalchemy import Column,String, Integer, ForeignKey
from database import Base


class NoteLike(Base):
    __tablename__ = "note_likes"
    
    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    note_id = Column(String, ForeignKey("notes.id"), primary_key=True)