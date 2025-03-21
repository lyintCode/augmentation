from uuid import uuid4
from types import SimpleNamespace
from typing import Callable

import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient
from zipfile import ZipFile
from io import BytesIO
from sqlalchemy.orm import Session

from app.models import User
from app.crud import update_image_task_status, create_image_task

def test_upload_invalid_file_type(client: TestClient, access_token: str):
    """Тест загрузки неверного типа файла"""

    # Тестовый текстовый файл, не изображение
    invalid_file = BytesIO(b"not_an_image")
    invalid_file.name = "invalid_file.txt"

    # Отправляем запрос
    headers = {"Authorization": f"Bearer {access_token}"}
    response = client.post(
        "/upload/",
        files={"files": ("test_image.txt", invalid_file, "text/plain")},
        headers=headers
    )

    assert response.status_code == 400    
    response_data = response.json()
    assert "Неподдерживаемое расширение" in response_data['detail']

@pytest.fixture()
def test_upload_image(client: TestClient, access_token: str, db_session: Session, test_user: User):
    """Тест загрузки изображения"""

    # Фейковые данные
    image_data = BytesIO(b"some_image_content")
    image_data.name = "image.png"
    fake_image_link = "http://minio:9000/images/image_original.png"

    # Мокаем celery задачу
    with patch("app.routers.tasks.process_image_task.delay") as mock_upload_to_minio:
        # Возвращаем фиктивный url
        mock_upload_to_minio.return_value = fake_image_link

        # Загрузка без авторизации
        response = client.post(
            "/upload/",
            files={"file": ("test_image.png", image_data, "image/png")}
        )
        assert response.status_code == 403
        assert response.json()["detail"] == "Not authenticated"

        # Загрузка с авторизацией
        headers = {"Authorization": f"Bearer {access_token}"}
        response = client.post(
            "/upload/",
            files={"files": ("test_image.png", image_data, "image/png")},
            headers=headers
        )

        # мок должен был быть вызван 1 раз
        mock_upload_to_minio.assert_called_once()

    response_data = response.json()
    task_id = response_data["task_ids"][0]

    # Добавляем задачу в бд
    create_image_task(
        db=db_session,
        task_id=task_id,
        img_link=fake_image_link,
        user_id=test_user.id
    )

    # Помечаем задачу завершенной
    update_image_task_status(db_session, task_id, status=True)

    # Проверяем ответ
    assert response.status_code == 200
    assert "message" in response_data
    assert response_data["message"] == "Задача создана"
    assert "task_ids" in response_data
    assert response_data["task_ids"][0]

    # Возвращаем id задачи для использования в других тестах
    return task_id

def test_get_task_status_success(
        client: TestClient, 
        access_token: str, 
        test_upload_image: str
    ):
    """
    Тест успешного получения статуса задачи.
    id заадачи берет из предыдущего теста
    """

    # Запрос статуса задачи по id
    headers = {"Authorization": f"Bearer {access_token}"}
    response = client.post(
        f"/status/{test_upload_image}",
        headers=headers
    )

    # Проверка ответ
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["task_id"] == test_upload_image
    assert response_data["status"] is True

def test_get_user_upload_history_success(
        client: TestClient, 
        access_token: str, 
        test_upload_image: str,
        test_user: User,
    ):
    """Тест успешного получения истории загрузок пользователя"""
    
    # Запрос задач пользователя по id
    headers = {"Authorization": f"Bearer {access_token}"}
    response = client.post(
        f"/history/{test_user.id}",
        headers=headers
    )
    
    response_data = response.json()

    assert response_data[0]['task_id'] == test_upload_image
    assert response_data[0]['img_link'] == "http://minio:9000/images/image_original.png"
    assert response_data[0]['user_id'] == test_user.id
    assert response_data[0]['status'] == True

def test_get_user_upload_history_unknown_user(
        client: TestClient, 
        access_token: str, 
    ):
    """
    Тест получения истории загрузок несуществующего пользователя.
    Должен дать ошибку доступа, потому что id пользователя не совпадает
    """

    random_user_id = str(uuid4())
    
    # Запрос задач пользователя по id
    headers = {"Authorization": f"Bearer {access_token}"}
    response = client.post(
        f"/history/{random_user_id}",
        headers=headers
    )
    
    response_data = response.json()

    assert response_data['detail'] == 'Ошибка доступа'
    
def test_download_task_images(
        client: TestClient, 
        test_upload_image: str, 
        mock_minio_files: Callable, 
        access_token: str
    ):
    """
    Тест скачивания изображений по id задачи zip-архивом
    """

    with patch("app.routers.tasks.download_file_from_minio", side_effect=mock_minio_files):

        headers = {"Authorization": f"Bearer {access_token}"}

        response = client.post(f"/task/{test_upload_image}", headers=headers)

        # Проверка ответа
        assert response.status_code == 200
        assert response.headers["Content-Type"] == "application/zip"           

        # Проверка соедержимого zip архива
        with ZipFile(BytesIO(response.content)) as zip_file:
            file_names = zip_file.namelist()
            assert len(file_names) == 4 # 4 изображения
            
            # Проверка всех типов изображений
            assert any("_original.png" in name for name in file_names), "Original не найден"
            assert any("_rotated.png" in name for name in file_names), "Rotated не найден"
            assert any("_gray.png" in name for name in file_names), "Gray не найден"
            assert any("_scaled.png" in name for name in file_names), "Scaled не найден"