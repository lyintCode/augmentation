from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError
from app.config import settings

DATABASE_URL = settings.DATABASE_URL

engine = create_engine(DATABASE_URL)

try:
    with engine.connect() as connection:
        print("DB is ready!")
except OperationalError:
    exit(1)