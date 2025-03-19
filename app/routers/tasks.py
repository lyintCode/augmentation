import os
from zipfile import ZipFile

from fastapi import (
    APIRouter, 
    Depends, 
    HTTPException, 
    UploadFile, 
    File, 
    Response
)
from sqlalchemy.orm import Session
from typing import List
from uuid import uuid4
from io import BytesIO
from tempfile import NamedTemporaryFile
from urllib.parse import urlparse

from app.crud import (
    create_image_task,
    get_image_task,
    get_image_tasks_by_user,
)
from app.database import get_db
from app.schemas import TaskResponse, UploadResponse
from app.auth import get_current_user
from app.models import User
from app.utils import (
    upload_to_minio, 
    download_file_from_minio, 
    validate_file_extension, 
    generate_file_name,
)
from app.config import settings
from app.celery import process_image_task

router = APIRouter()

@router.post("/upload", response_model=UploadResponse)
def upload_image(
    files: List[UploadFile] = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> UploadResponse:
    """Отправить список изображений для обработки"""

    task_ids = []
    for file in files:
        # Проверяем расширение файла
        validate_file_extension(file.filename)

        # Генерируем уникальный task_id
        task_id = str(uuid4())

        # Читаем содержимое файла
        file_content = file.file.read()

        # Генерируем имя файла для оригинального изображения
        original_file_name = generate_file_name(task_id, "original", file.filename)

        # Загружаем оригинальное изображение в MinIO
        img_link = upload_to_minio(BytesIO(file_content), original_file_name)

        # Сохраняем метаданные в базу данных
        img_link = f"http://{settings.MINIO_HOST}/{settings.MINIO_BUCKET_NAME}/{original_file_name}"
        task = create_image_task(
            db=db,
            task_id=task_id,
            img_link=img_link,
            user_id=current_user.id,
        )
        task_ids.append(task.task_id)

        # Добавляем задачу в Celery
        process_image_task.delay(task_id, file_content, file.filename)

    return {"message": "Tasks created", "task_ids": task_ids}

@router.post("/status/{task_id}", response_model=TaskResponse)
def get_task_status(
    task_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> TaskResponse:
    """Получить статус выполнения задачи по ID"""

    task = get_image_task(db, task_id=task_id)
    if not task or task.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Задача не найдена")
    
    return task

@router.post("/history/{user_id}", response_model=List[TaskResponse])
def get_user_history(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> List[TaskResponse]:
    """Получить историю обработанных изображений для данного user_id"""

    if user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Ошибка доступа")
    
    tasks = get_image_tasks_by_user(db, user_id=user_id)

    return tasks

@router.post("/task/{task_id}")
def download_task_images(
    task_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Скачать изображения по задаче ID в виде zip-архива"""

    task = get_image_task(db, task_id=task_id)
    if not task or task.user_id != current_user.id:
        return HTTPException(status_code=404, detail="Задача не найдена")
    
    # Создание временного zip файла
    with NamedTemporaryFile(suffix=".zip", delete=True) as temp_zip:
        with ZipFile(temp_zip.name, 'w') as zip_file:
            # Извлекаем расширение из img_link
            original_file_name = os.path.basename(urlparse(task.img_link).path)
            _, ext = os.path.splitext(original_file_name)

            for suffix in ["original", "rotated", "gray", "scaled"]:
                file_name = f"{task_id}_{suffix}{ext}"
                try:
                    data = download_file_from_minio(file_name)
                    if not data:
                        continue
                    zip_file.writestr(file_name, data)
                except:
                    continue  # Пропуск файлов, которых нет

        # Чтение содержимого временного файла
        with open(temp_zip.name, "rb") as f:
            zip_data = f.read()

    # Создание потока для скачивания
    response = Response(zip_data, media_type="application/zip")
    response.headers["Content-Disposition"] = f'attachment; filename={task_id}.zip'

    return response





