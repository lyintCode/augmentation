from typing import Dict

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.schemas import UserLogin, UserCreate, Token
from app.auth import authenticate_user, create_access_token
from app.crud import create_user, get_user_by_email
from app.database import get_db

router = APIRouter()

@router.post('/registration', response_model=Token)
def register(user: UserCreate, db: Session = Depends(get_db)) -> Dict[str, str]:
    """Регистрация пользователя и выдача JWT-токена"""

    # Проверка на уже созданного пользователя
    existing_user = get_user_by_email(db, user.email)
    if existing_user:
        raise HTTPException(status_code=400, detail='Email уже зарегистрирован')
    
    # Создаем пользователя
    created_user = create_user(db, user)
    
    # Создаем jwt-токен
    access_token = create_access_token(data={'sub': created_user.email})
    return {'access_token': access_token, 'token_type': 'bearer'}

@router.post("/login", response_model=Token)
def login(user_data: UserLogin, db: Session = Depends(get_db)) -> Dict[str, str]:
    """Аутентификация пользователя и выдача JWT-токена"""
    user = authenticate_user(db, user_data.email, user_data.password)

    if not user:
        raise HTTPException(
            status_code=401,
            detail='Неверный логин/пароль',
            headers={'WWW-Authenticate': 'Bearer'},
        )
    
    access_token = create_access_token(data={'sub': user.email})
    
    return {'access_token': access_token, 'token_type': 'bearer'}