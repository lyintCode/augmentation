from datetime import timedelta
from pathlib import Path
from typing import Callable, Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from app.models import User
from app.main import app
from app.database import get_db, Base
from app.crud import create_user
from app.schemas import UserCreate
from app.auth import create_access_token

# Тестовая sqlite бд
SQLALCHEMY_DATABASE_URL = 'sqlite:///./test.db'

engine = create_engine(SQLALCHEMY_DATABASE_URL)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture()
def db_session() -> Generator[Session, None, None]:
    """Фикстура для создания и управления тестовой БД"""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    db = TestingSessionLocal()

    try:
        yield db
    finally:
        db.close()

@pytest.fixture()
def client(db_session: Session) -> Generator[TestClient, None, None]:
    """Фикстура для тестового клиента FastAPI"""
    def override_get_db():
        try:
            yield db_session
        finally:
            db_session.close()

    app.dependency_overrides[get_db] = override_get_db

    yield TestClient(app)

@pytest.fixture(scope='function')
def test_user(db_session: Session) -> User:
    """Фикстура для создания тестового пользователя"""
    user_data = {
        'email': 'testuser@example.com',
        'password': 'password123'
    }
    new_user = create_user(db_session, UserCreate(**user_data))
    db_session.commit()
    return new_user

@pytest.fixture(scope="function")
def access_token(test_user: User) -> str:
    """
    Фикстура для создания JWT-токена для тестового пользователя
    """
    token = create_access_token(
        data={"sub": test_user.email},
        expires_delta=timedelta(minutes=30)
    )
    return token

@pytest.fixture
def mock_minio_files() -> Callable:
    """
    Фикстура для создания мока download_file_from_minio
    """
    results_dir = Path("tests/results")
    files = {
        "original": (results_dir / "image_original.png").read_bytes(),
        "rotated": (results_dir / "image_rotated.png").read_bytes(),
        "gray": (results_dir / "image_gray.png").read_bytes(),
        "scaled": (results_dir / "image_scaled.png").read_bytes(),
    }

    def mock_download_file_from_minio(file_name):
        """Извлекаем суффикс из имени файла"""
        suffix = file_name.split("_")[-1].split(".")[0]
        return files.get(suffix)

    return mock_download_file_from_minio