from sqlalchemy.orm import Session
from models import Users

class UsersRepository:
    
    def __init__(self, db:Session):
        self.db=db 
    
    def get_by_email(self, email: str) -> Users:
        return self.db.query(Users).filter(Users.email==email).first()
    
    def create(self, user_data: dict)->Users:
        new_user=Users(**user_data)
        self.db.add(new_user)
        self.db.commit()
        self.db.refresh(new_user)
        return new_user