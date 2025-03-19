from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError
import os

# Получаем строку подключения из переменной окружения
DATABASE_URL = "postgresql+psycopg2://admin:admin@db/augmentation"

# Создаём движок SQLAlchemy
engine = create_engine(DATABASE_URL)

try:
    with engine.connect() as connection:
        print("DB is ready!")
except OperationalError:
    exit(1)