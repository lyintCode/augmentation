from fastapi.testclient import TestClient

from app.schemas import UserCreate
from app.crud.users import create_user
from app.models import User

def test_create_user(db_session):
    """Тест создания пользователя."""
    
    user_data = {
        'email': 'testuser@example.com',
        'password': 'password123'
    }

    new_user = create_user(db_session, UserCreate(**user_data))

    assert new_user is not None
    assert new_user.email == user_data['email']

    # Чекаем пользователя в БД
    db_user = db_session.query(User).filter_by(email=user_data['email']).first()
    assert db_user is not None
    assert db_user.email == user_data['email']

def test_login(client: TestClient, test_user):
    """Тест авторизации пользователя"""
    
    login_data = {
        'email': 'testuser@example.com',
        'password': 'password123'
    }

    response = client.post('/login', json=login_data)

    assert response.status_code == 200

    # Проверяем содержимое ответа
    response_data = response.json()
    assert 'access_token' in response_data
    assert 'token_type' in response_data
    assert response_data['token_type'] == 'bearer'

    # Проверяем, что токен не пустой
    access_token = response_data['access_token']
    assert isinstance(access_token, str)
    assert len(access_token) > 0