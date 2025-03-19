from sqlalchemy import Column, String, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from uuid import uuid4
from datetime import datetime

Base = declarative_base()

class User(Base):
    """Модель пользователя"""
    __tablename__ = "users"

    id: str = Column(String, primary_key=True, default=lambda: str(uuid4()))
    email: str = Column(String, unique=True, index=True)
    hashed_password: str = Column(String)
    created_at: datetime = Column(DateTime, default=datetime.now())
    first_name: str = Column(String)
    last_name: str = Column(String)

    tasks = relationship("ImageTask", back_populates="user")

class ImageTask(Base):
    """Модель задачи обработки изображений"""
    __tablename__ = "image_tasks"

    id: str = Column(String, primary_key=True, default=lambda: str(uuid4()))
    task_id: str = Column(String, index=True)
    img_link: str = Column(String)
    created_at: datetime = Column(DateTime, default=datetime.now())
    status: bool = Column(Boolean, default=False)
    user_id: str = Column(String, ForeignKey("users.id"))

    user = relationship("User", back_populates="tasks")