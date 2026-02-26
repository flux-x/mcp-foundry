"""Alembic environment — async-compatible with all models registered."""

from logging.config import fileConfig

from sqlalchemy import create_engine, pool

import mcp_foundry.models.datasource  # noqa: F401
import mcp_foundry.models.mcp_server  # noqa: F401
import mcp_foundry.models.scraping_job  # noqa: F401
from alembic import context
from mcp_foundry.core.config import settings
from mcp_foundry.core.database import Base

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    url = settings.DATABASE_SYNC_URL
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = create_engine(settings.DATABASE_SYNC_URL, poolclass=pool.NullPool)
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
