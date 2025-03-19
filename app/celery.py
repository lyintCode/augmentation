from io import BytesIO
from celery import Celery

from app.utils import process_image, upload_to_minio, generate_file_name
from app.crud import update_image_task_status
from app.database import SessionLocal
from app.config import settings

# Инициализация Celery
celery_app = Celery("tasks", broker=settings.CELERY_BROKER_URL)

celery_app.conf.broker_connection_retry_on_startup = True

@celery_app.task
def process_image_task(task_id: str, file_content: bytes, filename: str):
    """
    Фоновая задача для обработки изображений.
    """
    db = SessionLocal()
    try:
        # Выполняем преобразования
        transformations = ["rotated", "gray", "scaled"]
        for suffix in transformations:
            transformed_content = process_image(file_content, suffix, filename)
            transformed_file_name = generate_file_name(task_id, suffix, filename)
            upload_to_minio(BytesIO(transformed_content), transformed_file_name)

        # Обновляем статус задачи на "завершено"
        update_image_task_status(db, task_id, status=True)

    except Exception as e:
        # В случае ошибки обновляем статус на "неудачно"
        update_image_task_status(db, task_id, status=False)
        raise e  # Логируем ошибку
    finally:
        db.close()