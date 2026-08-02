from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr


from database import get_db
from models import Users
from repositories.users_repository import UsersRepository
from services.users_service import UsersService


router = APIRouter(
    prefix="/api/auth",
    tags=["Authentication"],
)

def get_users_service(db: Session = Depends(get_db)) -> UsersService:
    repo = UsersRepository(db)
    return UsersService(repo)


class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

@router.post("/register", status_code=status.HTTP_201_CREATED)
def register_user(user: UserCreate, service:UsersService = Depends(get_users_service)):
    new_user = service.register_new_user(user.username, user.email, user.password)
    
    if not new_user:
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail="Email já em uso. Por favor, escolha outro email." 
        )
    return {"message": "Utilizador registado com sucesso", "user": new_user}
    
        
@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), service:UsersService = Depends(get_db) ):    
    
    token = service.authenticate_user(form_data.username, form_data.password)
    if not token:
        raise HTTPException(status_code = 400, details = "Credenciais de acesso inválidas")
    return {"access_token": token, "token_type": "bearer"}


