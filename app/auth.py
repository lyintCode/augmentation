from datetime import datetime, timedelta
from typing import Optional

from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status

from app.models import User
from app.config import settings
from app.crud import get_user_by_email
from app.database import get_db
from app.security import bearer_scheme

# Настройки для JWT
SECRET_KEY = settings.SECRET_KEY
SIGNATURE_ALGORITHM = settings.SIGNATURE_ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Генерация JWT-токена"""
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.now() + expires_delta
    else:
        expire = datetime.now() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({'exp': expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=SIGNATURE_ALGORITHM)

    return encoded_jwt

def authenticate_user(db: Session, email: str, password: str) -> User:
    """Аутентификация пользователя"""
    user = get_user_by_email(db, email)

    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Неверный логин/пароль',
            headers={'WWW-Authenticate': 'Bearer'},
        )
    
    return user

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Проверка пароля"""
    pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

    return pwd_context.verify(plain_password, hashed_password)

def get_current_user(
    token: str = Depends(bearer_scheme),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """Проверка JWT-токена и получение текущего пользователя"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail='Не удалось проверить учетные данные',
        headers={'WWW-Authenticate': 'Bearer'},
    )

    try:
        # Декодируем токен
        payload = jwt.decode(token.credentials, settings.SECRET_KEY, algorithms=[settings.SIGNATURE_ALGORITHM])
        email: str = payload.get('sub')
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    # Получаем пользователя из базы данных
    user = get_user_by_email(db, email=email)
    if user is None:
        raise credentials_exception
    
    return user

