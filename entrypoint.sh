#!/bin/sh

wait_for_postgres() {
  echo "Waiting for PostgreSQL to start..."
  until python check_db.py; do
    echo "Database is not ready yet. Retrying in 2 seconds..."
    sleep 2
  done
}

# Ждем полной инициализации postgresql
wait_for_postgres

# Применяем миграции Alembic
alembic upgrade head

# Запускаем приложение
exec "$@"