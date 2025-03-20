from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import List

class UserCreate(BaseModel):
    """Схема для регистрации пользователей"""
    email: EmailStr = Field(
        ...,
        min_length=8,
        json_schema_extra={"example": "user@gmail.com"}
    )
    password: str = Field(
        ...,
        min_length=8,
        json_schema_extra={"example": "Минимум 8 символов"}
    )
    first_name: str = Field(
        None,
        json_schema_extra={"example": "Иван"}
    )
    last_name: str = Field(
        None,
        json_schema_extra={"example": "Иванов"}
    )

class UserLogin(BaseModel):
    """Схема для авторизации пользователей"""
    email: EmailStr = Field(
        ..., 
        json_schema_extra={"example": "user@gmail.com"}
    )
    password: str = Field(
        ..., 
        json_schema_extra={"example": "password123"}
    )

class Token(BaseModel):
    """Схема для JWT-токена"""
    access_token: str = Field(
        ..., 
        json_schema_extra={"example": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."}
    )
    token_type: str = Field(
        ..., 
        json_schema_extra={"example": "bearer"}
    )

class TaskResponse(BaseModel):
    """
    Схема для ответа с данными задачи.
    """
    task_id: str = Field(
        ..., 
        json_schema_extra={"example": "42e5501f-b6e0-4113-94cb-537c4ff9ba95"}
    )
    img_link: str = Field(
        ..., 
        json_schema_extra={"example": "http://minio:9000/images/394d03fb-7e47-4e75-ba4f-4fef678af336_original.jpg"}
    )
    user_id: str = Field(
        ..., 
        json_schema_extra={"example": "42e5501f-b6e0-4113-94cb-537c4ff9ba95"}
    )
    created_at: datetime = Field(
        ..., 
        json_schema_extra={"example": "2025-03-20T10:00:00Z"}
    )
    status: bool = Field(
        ..., 
        json_schema_extra={"example": True}
    )

class UploadResponse(BaseModel):
    """
    Схема для ответа на загрузку изображений
    """
    message: str = Field(..., json_schema_extra={"example": "Изображения успешно загружены"})
    task_ids: List[str] = Field(..., json_schema_extra={"example": ["task1", "task2"]})