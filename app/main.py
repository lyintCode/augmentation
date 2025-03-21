from fastapi import FastAPI

from app.routers import auth_router, users_router, tasks_router

app = FastAPI()

# Подключаем маршруты
app.include_router(auth_router, tags=['auth'])
app.include_router(tasks_router, tags=['tasks'])
app.include_router(users_router, tags=['users'])