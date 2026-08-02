from repositories.user_repository import UsersRepository
from security import get_password_hash, verify_password, create_access_token

class UsersService:
    def __init__(self, repo: UsersRepository):
        self.repo = repo
        
    def register_new_user(self, username:str, email:str, password:str):
        existing_user = self.repo.get_by_email(email)
        if existing_user:
            return None
        
        hashed_password = get_password_hash(password)
        
        user_data = {
            "username": username,
            "email":    email,
            "passwoed": hashed_password
        }
        return self.repo.create(user_data)
    
    def authenticate_user(self, email:str, password:str):
        user = self.repo.get_by_email(email)
        if not user:
            return None
        if not verify_password(password, user.password):
            return None
        
        return create_access_token(data={"sub": user.email})