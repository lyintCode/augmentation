from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Session
from passlib.context import CryptContext

from app.models import User
from app.schemas import UserCreate

def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """Поиск пользователя по email"""
    return db.query(User).filter(User.email == email).first()

def get_password_hash(password: str) -> str:
    """Хэширование пароля"""
    pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
    
    return pwd_context.hash(password)

def create_user(db: Session, user: UserCreate) -> User:
    """Создание пользователя"""
    hashed_password = get_password_hash(user.password)
    db_user = User(
        email=user.email,
        hashed_password=hashed_password,
        first_name=user.first_name,
        last_name=user.last_name,
        created_at=datetime.now()
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user