from fastapi import HTTPException, File
from minio import Minio
from minio.error import S3Error
from app.config import settings

BUCKET_NAME = settings.MINIO_BUCKET_NAME
MINIO_HOST = settings.MINIO_HOST
MINIO_USERNAME = settings.MINIO_USERNAME
MINIO_PASSWORD = settings.MINIO_PASSWORD

# Настройка клиента Minio
minio_client = Minio(
    MINIO_HOST,
    access_key=MINIO_USERNAME,
    secret_key=MINIO_PASSWORD,
    secure=False
)

def upload_to_minio(file_content: File, file_name: str) -> str:
    """Загрузка файла в Minio"""
    try:
        
        # Создаём бакет, если его нет
        if not minio_client.bucket_exists(BUCKET_NAME):
            minio_client.make_bucket(BUCKET_NAME)
            
        # Проверяем, что file_content не пустой
        if not file_content or file_content.getbuffer().nbytes == 0:
            raise ValueError("Файл пустой")

        # Загружаем файл
        minio_client.put_object(
            BUCKET_NAME,
            file_name,
            file_content,
            length=-1,  # Автоматически определяется длина
            part_size=10 * 1024 * 1024  # Размер части для загрузки
        )

        # Генерируем URL
        img_link = f"http://{MINIO_HOST}/{BUCKET_NAME}/{file_name}"

        return img_link

    except Exception as e:
        
        raise HTTPException(status_code=500, detail=f"MinIO error: {e}")
    
def download_file_from_minio(file_name):
    """Скачивание файла из MinIO."""
    try:
        # Скачиваем файл
        data = minio_client.get_object(BUCKET_NAME, file_name).read()
        return data
    except S3Error as e:
        raise Exception(f"MinIO error: {e}")
    except Exception as e:
        raise Exception(f"Unexpected error: {e}")