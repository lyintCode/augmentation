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

if [ "$RUN_TESTS" = "true" ]; then
  echo "Запускаем тесты..."

  # Запуск pytest и проверка статуса выполнения
  if pytest; then
    echo -e "\e[32mВсе тесты прошли успешно!\e[0m"
  else
    echo -e "\e[31m\nОшибки при выполнении тестов!\n\e[0m"
  fi

fi

# Запускаем приложение
exec "$@"