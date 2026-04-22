from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta
from pydantic import BaseModel
from schemas import UserCreate, UserResponse, Token
from models import User
from database import get_db
from auth import get_password_hash, create_access_token, verify_password
from config import get_settings

router = APIRouter(prefix="/api/v2/auth", tags=["auth"])
settings = get_settings()


class LoginRequest(BaseModel):
    """Schema para requisição de login"""
    username: str
    password: str


@router.post("/register", response_model=UserResponse, status_code=201)
def register(user: UserCreate, db: Session = Depends(get_db)):
    """
    Registra um novo usuário
    
    **Segurança**: Senha será hasheada com bcrypt
    """

    # Verifica se o usuário já existe
    db_user = db.query(User).filter(
        (User.username == user.username)
    ).first()
    
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Usuário já cadastrado"
        )
    
    # Cria novo usuário com senha hasheada
    hashed_password = get_password_hash(user.password)
    db_user = User(
        username=user.username,
        hashed_password=hashed_password,
        is_admin=False
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return db_user


@router.post("/login", response_model=Token)
def login(credentials: LoginRequest, db: Session = Depends(get_db)):
    """
    Faz login e retorna um token JWT
    
    **Segurança**: 
    - Credenciais devem ser enviadas no BODY (POST), nunca na URL
    - Senha NUNCA é armazenada em logs
    - Token expira em tempo configurável
    """
    
    # Procura o usuário no banco
    user = db.query(User).filter(User.username == credentials.username).first()
    
    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário ou senha inválidos"
        )
    
    # Cria token de acesso
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}
