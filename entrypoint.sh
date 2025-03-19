#!/bin/sh

# Ждём, пока PostgreSQL будет готов
until alembic current; do
  echo "Waiting for database to start..."
  sleep 2
done

# Применяем миграции Alembic
alembic upgrade head

# Запускаем приложение
exec "$@"