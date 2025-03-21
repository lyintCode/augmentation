#!/bin/sh

wait_for_postgres() {
  echo "Waiting for PostgreSQL to start..."
  until python check_db.py; do
    echo "Database is not ready yet. Retrying in 2 seconds..."
    sleep 2
  done
}

# Ожидание полной инициализации postgresql
wait_for_postgres

# Проверяем, есть ли миграции в папке versions
if [ -z "$(ls -A /app/migrations/versions)" ]; then
  # Генерируем начальную миграцию
  alembic revision --autogenerate -m "Initial migration"
fi

# Применение миграции Alembic
alembic upgrade head

# Запуск приложения
exec "$@"