from pathlib import Path
from app.utils import process_image
from tests.image import TEST_IMAGE_BYTES

def test_image_transform():
    """Тест преобразования изображений"""

    # Создаем директорию для результатов
    results_dir = Path("tests/results")
    results_dir.mkdir(parents=True, exist_ok=True)

    # Сохраняем оригинальное изображение в файл
    original_image_path = results_dir / "image_original.png"
    with open(original_image_path, "wb") as f:
        f.write(TEST_IMAGE_BYTES)

    # Определяем пути для сохранения результатов
    rotated_image_path = results_dir / "image_rotated.png"
    gray_image_path = results_dir / "image_gray.png"
    scaled_image_path = results_dir / "image_scaled.png"

    # Преобразование: оттенки серого
    gray_image = process_image(TEST_IMAGE_BYTES, suffix="gray", original_filename="test_image.png")
    with open(gray_image_path, "wb") as f:
        f.write(gray_image)

    # Преобразование: поворот
    rotated_image = process_image(TEST_IMAGE_BYTES, suffix="rotated", original_filename="test_image.png")
    with open(rotated_image_path, "wb") as f:
        f.write(rotated_image)

    # Преобразование: масштабирование
    scaled_image = process_image(TEST_IMAGE_BYTES, suffix="scaled", original_filename="test_image.png")
    with open(scaled_image_path, "wb") as f:
        f.write(scaled_image)

    # Проверяем, что файлы созданы
    assert original_image_path.exists()
    assert rotated_image_path.exists()
    assert gray_image_path.exists()
    assert scaled_image_path.exists()