import importlib
import os
from logging.config import fileConfig
from typing import Optional
from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context
from sqlalchemy.ext.declarative import declarative_base

from config.ConfigLoader import ConfigLoader

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
bot_config = ConfigLoader()
db_config = bot_config.database
config = context.config
Base = declarative_base()

def format_db_url(db_host: str, db_port: int, db_user: str, db_password: str, db_name: str, dialect: str = "postgresql", driver: Optional[str] = None):
    driver_part = f"+{driver}" if driver else ""
    return f"{dialect}{driver_part}://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"

# Automatically discover and load models from the `models` package
def load_metadata_from_models():
    from sqlalchemy.ext.declarative import DeclarativeMeta
    # Discover all modules in the models package
    models_package = "models"
    for module_name in os.listdir(models_package):
        if module_name.endswith(".py") and module_name != "__init__.py":
            importlib.import_module(f"{models_package}.{module_name[:-3]}")

    # Ensure Base.metadata collects all model tables
    return Base.metadata


# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
target_metadata = load_metadata_from_models()

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = format_db_url(db_config.DB_URL, db_config.DB_PORT, db_config.DB_USER, db_config.DB_PASSWORD, db_config.DB_DBNAME, driver="psycopg2")
    config.set_main_option("sqlalchemy.url", url)
    context.configure(
        url=url,
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
    url = format_db_url(db_config.DB_URL, db_config.DB_PORT, db_config.DB_USER, db_config.DB_PASSWORD, db_config.DB_DBNAME, driver="psycopg2")
    config.set_main_option("sqlalchemy.url", url)
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
