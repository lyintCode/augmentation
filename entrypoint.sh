#!/bin/sh

wait_for_postgres() {
  # Функция ожидания полного запуска контейнера postgresql
  echo "Ожидание запуска PostgreSQL ..."
  until python check_db.py; do
    echo "DB еще не готова. Повторная проверка через 2 сек ..."
    sleep 2
  done
}

wait_for_postgres

# Проверяем, есть ли миграции в папке versions
if [ -z "$(ls -A /app/migrations/versions)" ]; then
  # Генерируем начальную миграцию
  alembic revision --autogenerate -m "Initial migration"
fi

# Применение миграции Alembic
alembic upgrade head

exec "$@"