from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DB_NAME: str
    DB_USERNAME: str
    DB_PASSWORD: str
    DATABASE_URL: str
    REDIS_HOST: str
    SECRET_KEY: str
    SIGNATURE_ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    MINIO_HOST: str
    MINIO_USERNAME: str
    MINIO_PASSWORD: str
    MINIO_BUCKET_NAME: str
    CELERY_BROKER_URL: str

    class Config:
        env_file = ".env"

settings = Settings()