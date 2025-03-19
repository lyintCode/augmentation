# Базовый образ Python
FROM python:3.11-slim

ARG USER_ID=1000
ARG GROUP_ID=1000

# Создание группы и пользователя
RUN groupadd -g $GROUP_ID appuser && \
    useradd -m -u $USER_ID -g $GROUP_ID appuser

WORKDIR /app

# Создаем и активируем виртуальное окружение
RUN python3 -m venv /home/appuser/venv
ENV PATH="/home/appuser/venv/bin:$PATH"

# Копируем и устанавливаем зависимости
COPY requirements.txt .
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Копируем исходники проекта
COPY . .

# Смена владельца файлов
RUN chown -R appuser:appuser /app

# Запускаем контейнер от обычного пользователя
USER appuser

# Команда для запуска приложения
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]