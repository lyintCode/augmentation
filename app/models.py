from sqlalchemy import Column, String, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from uuid import uuid4
from datetime import datetime

from app.database import Base

class User(Base):
    """Модель пользователя"""
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    created_at = Column(DateTime, default=datetime.now())
    first_name = Column(String)
    last_name = Column(String)

    tasks = relationship("ImageTask", back_populates="user")

class ImageTask(Base):
    """Модель задачи обработки изображений"""
    __tablename__ = "image_tasks"

    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    task_id = Column(String, index=True)
    img_link = Column(String)
    created_at = Column(DateTime, default=datetime.now())
    status = Column(Boolean, default=False)
    user_id = Column(String, ForeignKey("users.id"))

    user = relationship("User", back_populates="tasks")