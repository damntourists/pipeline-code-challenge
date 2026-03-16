import os
import sys
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context

# 1. Path setup
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(current_dir, ".."))
sys.path.append(os.path.join(parent_dir, "src"))

# 2. Model Imports (Ensures Base.metadata is populated)
from assets.db.models.base import Base
from assets.db.models.asset import Asset
from assets.db.models.asset_version import AssetVersion

# 3. Standard Alembic setup
config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata
DB_URL = os.getenv("DATABASE_URL", "mysql+pymysql://dbuser:Password123@db:3306/asset_db")

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode (outputs SQL scripts)."""
    print("Running migrations in 'offline' mode.")
    context.configure(
        url=DB_URL,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    """Run migrations in 'online' mode (connects to DB)."""
    print("Running migrations in 'online' mode.")
    conf = config.get_section(config.config_ini_section, {})
    conf["sqlalchemy.url"] = DB_URL

    engine = engine_from_config(
        conf,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool
    )

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