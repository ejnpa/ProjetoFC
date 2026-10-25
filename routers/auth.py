from fastapi import APIRouter, Depends, HTTPException, status , Response
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr

from database import get_db
from repositories.users_repository import UsersRepository
from services.user_service import UsersService
from security import get_password_hash

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
def login(response: Response = None,
          form_data: OAuth2PasswordRequestForm = Depends(),
          service:UsersService = Depends(get_users_service)         
):
    token = service.authenticate_user(form_data.username, form_data.password)
    
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou password inválidos",
        )
    
    response.set_cookie (
        key = "access_token",
        value = token,
        httponly = True,
        samesite = "lax",
        secure = False,  # Definir como True se usar HTTPS
        max_age = 60*60*24  # 1 dia
    )
    
    return {"message": "Login efetuado com sucesso", "username": form_data.username}

@router.post("/logout")
def logout(response: Response):
    response.delete_cookie(key = "access_token")
    return {"message": "Sessão terminada"}
