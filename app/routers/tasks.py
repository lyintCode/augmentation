import os
from zipfile import ZipFile
from typing import List
from uuid import uuid4
from tempfile import NamedTemporaryFile

from fastapi import (
    APIRouter, 
    Depends, 
    HTTPException, 
    UploadFile, 
    File, 
    Response
)
from sqlalchemy.orm import Session
from urllib.parse import urlparse

from app.crud import (
    get_image_task,
    get_image_tasks_by_user,
)
from app.database import get_db
from app.schemas import TaskResponse, UploadResponse
from app.auth import get_current_user
from app.models import User, ImageTask
from app.utils import (
    download_file_from_minio, 
    validate_file_extension, 
)
from app.config import settings
from app.celery import process_image_task

router = APIRouter()

@router.post('/upload', response_model=UploadResponse)
def upload_image(
    files: List[UploadFile] = File(...),
    current_user: User = Depends(get_current_user),
) -> UploadResponse:
    """Отправить список изображений для обработки"""

    task_ids = []
    for file in files:
        if file.filename is None:
            raise HTTPException(status_code=400, detail="Ошибка получения имени файла")
        
        # Проверяем расширение файла
        validate_file_extension(file.filename)

        # Генерируем task_id
        task_id = str(uuid4())

        # Содержимое файла
        file_content = file.file.read()

        # Добавляем задачу в Celery
        process_image_task.delay(current_user.id, task_id, file_content, file.filename)

        task_ids.append(task_id)

    return UploadResponse(message="Задача создана", task_ids=task_ids)

@router.post('/status/{task_id}', response_model=TaskResponse)
def get_task_status(
    task_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> ImageTask:
    """Получить статус выполнения задачи по ID"""

    task = get_image_task(db, task_id=task_id)

    if not task or task.user_id != current_user.id:
        raise HTTPException(status_code=404, detail='Задача не найдена')
    
    return task

@router.post('/history/{user_id}', response_model=List[TaskResponse])
def get_user_history(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> List[ImageTask]:
    """Получить историю обработанных изображений для данного user_id"""

    if user_id != current_user.id:
        raise HTTPException(status_code=403, detail='Ошибка доступа')
    
    tasks = get_image_tasks_by_user(db, user_id=user_id)

    return tasks

@router.post('/task/{task_id}')
def download_task_images(
    task_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Response | HTTPException:
    """Скачать изображения по ID задачи в виде zip-архива"""

    task = get_image_task(db, task_id=task_id)
    if not task or task.user_id != current_user.id:
        return HTTPException(status_code=404, detail='Задача не найдена')
    
    # Создание временного zip
    with NamedTemporaryFile(suffix='.zip', delete=True) as temp_zip:
        with ZipFile(temp_zip.name, 'w') as zip_file:

            # Извлекаем расширение из img_link
            original_file_name = os.path.basename(urlparse(task.img_link).path)
            _, ext = os.path.splitext(original_file_name)

            # Скачиваем трансформированные файлы с минио
            for suffix in ['original', 'rotated', 'gray', 'scaled']:
                # mypy ругался на то, что ext может быть bytes
                if isinstance(ext, bytes):
                    ext = ext.decode('utf-8')
                file_name = f'{task_id}_{suffix}{ext}'
                try:
                    data = download_file_from_minio(file_name)
                    if not data:
                        continue
                    zip_file.writestr(file_name, data)
                except:
                    continue

        # Чтение содержимого временного файла
        with open(temp_zip.name, 'rb') as f:
            zip_data = f.read()

    response = Response(zip_data, media_type='application/zip')
    response.headers['Content-Disposition'] = f'attachment; filename={task_id}.zip'

    return response
