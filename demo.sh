#!/bin/bash

# Проверка наличия jq
if ! command -v jq &> /dev/null; then
    echo "Утилита jq не найдена. Установите её с помощью 'sudo apt install jq'"
    exit 1
fi

BASE_URL="http://localhost:8000"

echo "=== Демонстрация работы API ==="

echo "1. Регистрация нового пользователя..."
REGISTER_RESPONSE=$(curl -s -X POST "$BASE_URL/registration" \
    -H "Content-Type: application/json" \
    -d '{
        "email": "testuser@example.com",
        "password": "password123",
        "first_name": "John",
        "last_name": "Doe"
    }')
echo -e "Ответ на регистрацию: $REGISTER_RESPONSE\n"

echo "2. Авторизация пользователя..."
LOGIN_RESPONSE=$(curl -s -X POST "$BASE_URL/login" \
    -H "Content-Type: application/json" \
    -d '{
        "email": "testuser@example.com",
        "password": "password123"
    }')
echo -e "Ответ на авторизацию: $LOGIN_RESPONSE\n"

ACCESS_TOKEN=$(echo "$LOGIN_RESPONSE" | jq -r '.access_token')
if [ -z "$ACCESS_TOKEN" ]; then
    echo "Ошибка авторизации. Проверьте данные."
    exit 1
fi
echo -e "Токен доступа: $ACCESS_TOKEN\n"

echo "3. Загрузка изображения..."
UPLOAD_RESPONSE=$(curl -s -X POST "$BASE_URL/upload" \
    -H "Authorization: Bearer $ACCESS_TOKEN" \
    -F "files=@./test_image.png")
echo $UPLOAD_RESPONSE

TASK_ID=$(echo "$UPLOAD_RESPONSE" | jq -r '.task_ids[0]')
if [ -z "$TASK_ID" ]; then
    echo "Ошибка загрузки изображения."
    exit 1
fi
echo -e "Идентификатор задачи: $TASK_ID\n"

echo "Ожидание 2 сек для окончния задачи celery ..."
sleep 2

echo "4. Проверка статуса задачи..."
STATUS_RESPONSE=$(curl -s -X POST "$BASE_URL/status/$TASK_ID" \
    -H "Authorization: Bearer $ACCESS_TOKEN")
echo -e "Статус задачи: $STATUS_RESPONSE\n"

USER_ID=$(echo "$STATUS_RESPONSE" | jq -r '.user_id')
if [ -z "$USER_ID" ]; then
    echo "Ошибка получение id пользователя."
    exit 1
fi
echo -e "ID пользователя: $USER_ID\n"

echo "5. Получение истории пользователя..."
HISTORY_RESPONSE=$(curl -s -X POST "$BASE_URL/history/$USER_ID" \
    -H "Authorization: Bearer $ACCESS_TOKEN")
echo -e "История пользователя: $HISTORY_RESPONSE\n"

echo "6. Скачивание результатов задачи..."
DOWNLOAD_RESPONSE=$(curl -s -X POST "$BASE_URL/task/$TASK_ID" \
    -H "Authorization: Bearer $ACCESS_TOKEN" \
    --output "demo_$TASK_ID.zip")
if [ $? -eq 0 ]; then
    echo -e "Результаты задачи успешно скачаны: demo_$TASK_ID.zip\n"
else
    echo -e "Ошибка скачивания результатов задачи\n"
fi

echo "=== Демонстрация завершена ==="