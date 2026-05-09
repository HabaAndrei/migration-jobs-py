import asyncio
from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import create_async_engine
from alembic import context

from database.models.utils import Base  # Declarative base
from database.db_client import ASYNC_DATABASE_URL  # Async database URL

# Alembic Config object for .ini file access
config = context.config

# Configure Python logging from config file
fileConfig(config.config_file_name)

# Target metadata for autogenerate support
target_metadata = Base.metadata


def run_migrations_offline():
    """Run migrations in 'offline' mode."""
    url = ASYNC_DATABASE_URL
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection):
    """Run migrations using a synchronous connection (used inside async wrapper)."""
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online():
    """Run migrations in 'online' mode using AsyncEngine."""
    connectable = create_async_engine(ASYNC_DATABASE_URL, poolclass=pool.NullPool)

    async with connectable.connect() as connection:
        # Alembic expects a sync Connection, so wrap it
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())