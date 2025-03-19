from os.path import splitext
from fastapi import HTTPException
from PIL import Image, UnidentifiedImageError
from typing import Generator
from io import BytesIO

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png"}

def iterfile(zip_filename:str) -> Generator[bytes, None, None]:
    """
    Читает zip архив по частям 
    и возвращает его содержимое
    как генератор байтов
    """
    with open(zip_filename, "rb") as f:
        yield from f

def validate_file_extension(filename: str) -> None:
    """
    Проверяет, что расширение файла допустимо
    """
    ext = splitext(filename)[1].lower()  # Получаем расширение файла
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400, 
            detail=f"Неподдерживаемое расширение файла: {ext}. Разрешенные расширения: {', '.join(ALLOWED_EXTENSIONS)}"
        )
    
def generate_file_name(task_id: str, suffix: str, original_filename: str) -> str:
    """
    Генерирует имя файла для сохранения в MinIO
    """
    ext = splitext(original_filename)[1].lower()
    return f"{task_id}_{suffix}{ext}"

def process_image(image_content: bytes, suffix: str, original_filename: str) -> bytes:
    """
    Выполняет преобразование изображения.
    """
    if not image_content or len(image_content) == 0:
        raise ValueError("Image content is empty.")

    try:
        # Открываем изображение из байтов
        image = Image.open(BytesIO(image_content))

        if suffix == "rotated":
            # Поворот на 90 градусов
            image = image.rotate(90, expand=True)
        elif suffix == "gray":
            # Преобразование в оттенки серого
            image = image.convert("L")
        elif suffix == "scaled":
            # Изменение размера в 2 раза с сохранением пропорций
            width, height = image.size
            new_size = (width // 2, height // 2)

            resampling_filter = getattr(Image, "Resampling", None)
            if resampling_filter:
                resampling_filter = resampling_filter.LANCZOS
            else:
                resampling_filter = Image.ANTIALIAS

            image = image.resize(new_size, resampling_filter)

        # Определяем формат файла из оригинального имени
        ext = splitext(original_filename)[1].lower()
        format = None
        if ext in [".jpg", ".jpeg"]:
            format = "JPEG"
        elif ext in [".png"]:
            format = "PNG"
        else:
            raise ValueError(f"Неподдерживаемое расширение файла: {ext}")

        # Сохраняем изображение в байты
        output = BytesIO()
        image.save(output, format=format)
        return output.getvalue()

    except UnidentifiedImageError as e:
        raise ValueError(f"Ошибка идентификации изобюражения. Подробно: {e}")
    except Exception as e:
        raise ValueError(f"Ошибка обработки изображения: {e}")