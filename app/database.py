from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.config import settings

# Движок для подключения к базе данных
engine = create_engine(settings.DATABASE_URL)

# Фабрика сессий
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Предоставляет сессию базы данных
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()