import os
from logging.config import fileConfig
from typing import cast

from sqlalchemy import create_engine, pool
from alembic import context
from dotenv import load_dotenv

from app.models import Base

# Загружаем переменные окружения из .env
load_dotenv()

# URL для подключения к базе данных
DB_URL = cast(str, os.getenv('DATABASE_URL'))
if not DB_URL:
    raise ValueError("DATABASE_URL не задан в .env файле!")

config = context.config
config.set_main_option("sqlalchemy.url", DB_URL)

target_metadata = Base.metadata

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    context.configure(
        url=config.get_main_option("sqlalchemy.url"),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    engine = create_engine(DB_URL, poolclass=pool.NullPool)

    with engine.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
