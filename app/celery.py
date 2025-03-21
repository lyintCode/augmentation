from io import BytesIO

from celery import Celery

from app.utils import process_image, upload_to_minio, generate_file_name
from app.crud import update_image_task_status, create_image_task
from app.database import SessionLocal
from app.config import settings

# Инициализация Celery
celery_app = Celery('tasks', broker=settings.CELERY_BROKER_URL)

celery_app.conf.broker_connection_retry_on_startup = True

@celery_app.task
def process_image_task(user_id: str, task_id: str, file_content: bytes, filename: str) -> None:
    """Фоновая задача для обработки изображений"""
    db = SessionLocal()

    try:
        # Загружаем оригинальное изображение в MinIO
        original_file_name = generate_file_name(task_id, 'original', filename)
        img_link = upload_to_minio(BytesIO(file_content), original_file_name)

        # Сохраняем метаданные в базу данных
        create_image_task(
            db=db,
            task_id=task_id,
            img_link=img_link,
            user_id=user_id
        )

        # Выполняем преобразования
        transformations = ['rotated', 'gray', 'scaled']
        for suffix in transformations:
            transformed_content = process_image(file_content, suffix, filename)
            transformed_file_name = generate_file_name(task_id, suffix, filename)
            upload_to_minio(BytesIO(transformed_content), transformed_file_name)

        # Обновляем статус задачи на True (завершено)
        update_image_task_status(db, task_id, status=True)

    except Exception as e:
        # В случае ошибки возвращаем статус false
        update_image_task_status(db, task_id, status=False)
        raise e
    
    finally:
        db.close()