from fastapi.security import HTTPBearer

# Создаем экземпляр HTTPBearer для получения токена из запроса
bearer_scheme = HTTPBearer()