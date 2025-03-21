import os
from typing import Generator
from io import BytesIO

from fastapi import HTTPException
from PIL import Image, UnidentifiedImageError

FORMAT_MAPPING = {
    '.jpg': 'JPEG',
    '.jpeg': 'JPEG',
    '.png': 'PNG',
}

def iterfile(zip_filename:str) -> Generator[bytes, None, None]:
    """
    Читает zip архив по частям 
    и возвращает его содержимое
    как генератор байтов
    """
    with open(zip_filename, 'rb') as f:
        yield from f

def validate_file_extension(filename: str) -> None:
    """Проверяет, что расширение файла допустимо"""
    ext = os.path.splitext(filename)[1].lower()

    if ext not in FORMAT_MAPPING:
        raise HTTPException(
            status_code=400, 
            detail=f'Неподдерживаемое расширение: {ext}. Разрешенные расширения: {", ".join(FORMAT_MAPPING.keys())}'
        )
    
def generate_file_name(task_id: str, suffix: str, original_filename: str) -> str:
    """Генерирует имя файла для сохранения в MinIO"""
    ext = os.path.splitext(original_filename)[1].lower()
    return f'{task_id}_{suffix}{ext}'

def process_image(image_content: bytes, suffix: str, original_filename: str) -> bytes:
    """Выполняет преобразования изображений"""
    if not image_content or len(image_content) == 0:
        raise ValueError('Image content is empty.')

    try:
        image = Image.open(BytesIO(image_content))

        if suffix == 'rotated':
            # Поворот на 90 градусов
            image = image.rotate(90, expand=True)

        elif suffix == 'gray':
            # Преобразование в оттенки серого
            image = image.convert('L')

        elif suffix == 'scaled':
            # Изменение размера в 2 раза с сохранением пропорций
            width, height = image.size
            new_size = (width // 2, height // 2)

            resampling_filter = getattr(Image, 'Resampling', None)
            if resampling_filter:
                resampling_filter = resampling_filter.LANCZOS
            else:
                resampling_filter = Image.ANTIALIAS

            image = image.resize(new_size, resampling_filter)

        # Определяем формат файла из оригинального имени
        ext = os.path.splitext(original_filename)[1].lower()

        format = FORMAT_MAPPING.get(ext)
        if not format:
            raise ValueError(f'Неподдерживаемое расширение файла: {ext}')

        # Сохраняем изображение в байты
        output = BytesIO()
        image.save(output, format=format)
        return output.getvalue()

    except UnidentifiedImageError as e:
        raise ValueError(f'Ошибка идентификации изобюражения. Подробно: {e}')
    except Exception as e:
        raise ValueError(f'Ошибка обработки изображения: {e}')