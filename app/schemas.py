from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import List

class UserCreate(BaseModel):
    """Схема для регистрации пользователей"""
    email: EmailStr = Field(..., min_length=8, example="user@gmail.com")
    password: str = Field(..., min_length=8, example="Минимум 8 символов")
    first_name: str = Field(None, example="Иван")
    last_name: str = Field(None, example="Иванов")

class UserLogin(BaseModel):
    """Схема для авторизации пользователей"""
    email: EmailStr
    password: str

class Token(BaseModel):
    """Схема для JWT-токена"""
    access_token: str
    token_type: str

class TaskResponse(BaseModel):
    """
    Схема для ответа с данными задачи.
    """
    task_id: str
    img_link: str
    user_id: str
    created_at: datetime
    status: bool

class UploadResponse(BaseModel):
    """
    Схема для ответа на загрузку изображений
    """
    message: str
    task_ids: List[str]

