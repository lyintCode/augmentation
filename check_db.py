import os

from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError
from dotenv import load_dotenv

# Загружаем переменные окружения из .env
load_dotenv()

DB_URL = os.getenv('DATABASE_URL')
if not DB_URL:
    raise ValueError("DATABASE_URL не задан в .env файле!")

engine = create_engine(DB_URL)

try:
    with engine.connect() as connection:
        print("DB is ready!")
except OperationalError:
    exit(1)