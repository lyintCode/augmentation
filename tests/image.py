import base64

"""
Прозрачное изображение png 2x2 пикселя
для теста трансформации изображения
"""

TEST_IMAGE_BASE64 = (
    "iVBORw0KGgoAAAANSUhEUgAAAAIAAAACCAYAAABytg0kAAAAEUlEQVR42mP8z8AARIQB46gJAwAAAABJRU5ErkJggg=="
)

# Декодируем Base64 в байты
TEST_IMAGE_BYTES = base64.b64decode(TEST_IMAGE_BASE64)