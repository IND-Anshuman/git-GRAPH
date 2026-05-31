import os

wt_dir = r"C:\Users\HP\.gemini\antigravity\brain\574aac01-9eae-4701-9d04-989026299d75\.system_generated\worktrees\subagent-Config---Testing-Engineer-config-testing-engineer-f80529ce"

def create_file(rel_path, content):
    full_path = os.path.join(wt_dir, rel_path)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, "w", encoding="utf-8", newline="\n") as f:
        f.write(content.strip() + "\n")
    print(f"Created {rel_path}")

# 1. pyproject.toml
create_file("pyproject.toml", """
[project]
name = "git-graph"
version = "0.1.0"
description = "Temporal Code Knowledge Graph Platform"
requires-python = ">=3.12"
dependencies = [
    "fastapi>=0.115.0",
    "uvicorn[standard]>=0.30.0",
    "pydantic>=2.7.0",
    "pydantic-settings>=2.2.0",
    "sqlalchemy>=2.0.30",
    "psycopg2-binary>=2.9.9",
    "alembic>=1.13.0",
    "gitpython>=3.1.43",
    "tree-sitter>=0.23.0",
    "tree-sitter-python>=0.23.0",
    "structlog>=24.2.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.2.0",
    "pytest-cov>=5.0.0",
    "pytest-asyncio>=0.23.0",
    "black>=24.4.0",
    "ruff>=0.4.4",
    "mypy>=1.10.0",
    "httpx>=0.27.0",
]

[tool.ruff]
line-length = 88
target-version = "py312"

[tool.ruff.lint]
select = ["E", "F", "I", "N", "UP", "B", "C4", "RUF"]

[tool.black]
line-length = 88
target-version = ['py312']

[tool.mypy]
python_version = "3.12"
strict = false
warn_return_any = true
warn_unused_configs = true
ignore_missing_imports = true

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = "-v --tb=short"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
""")

# 2. src/config.py
create_file("src/config.py", """
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    environment: str = "local"
    debug: bool = False
    database_url: str = "postgresql://postgres:postgres@localhost:5432/git_graph_dev"
    storage_root: str = "./data/repositories"
    allowed_origins: list[str] = ["http://localhost:3000"]
    log_level: str = "INFO"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()
""")

# 3. .env.example
create_file(".env.example", """
ENVIRONMENT=local
DEBUG=True
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/git_graph_dev
STORAGE_ROOT=./data/repositories
ALLOWED_ORIGINS=["http://localhost:3000"]
LOG_LEVEL=INFO
""")

# 4. docker-compose.yml
create_file("docker-compose.yml", """
version: '3.8'

services:
  postgres:
    image: postgres:16
    environment:
      POSTGRES_DB: git_graph_dev
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres -d git_graph_dev"]
      interval: 5s
      timeout: 5s
      retries: 5

volumes:
  postgres_data:
""")

# 5. alembic.ini
create_file("alembic.ini", """
[alembic]
script_location = migrations
prepend_sys_path = .
version_path_separator = os
sqlalchemy.url = postgresql://postgres:postgres@localhost:5432/git_graph_dev

[loggers]
keys = root,sqlalchemy,alembic

[handlers]
keys = console

[formatters]
keys = generic

[logger_root]
level = WARN
handlers = console
qualname =

[logger_sqlalchemy]
level = WARN
handlers =
qualname = sqlalchemy.engine

[logger_alembic]
level = INFO
handlers =
qualname = alembic

[handler_console]
class = StreamHandler
args = (sys.stderr,)
level = NOTSET
formatter = generic

[formatter_generic]
format = %(levelname)-5.5s [%(name)s] %(message)s
datefmt = %H:%M:%S
""")

# 6. migrations/env.py
create_file("migrations/env.py", """
from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

from src.config import settings
try:
    from src.infrastructure.persistence.models.base import Base
    target_metadata = Base.metadata
except ImportError:
    target_metadata = None

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

def run_migrations_offline() -> None:
    url = settings.database_url
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    configuration = config.get_section(config.config_ini_section, {})
    configuration["sqlalchemy.url"] = settings.database_url
    
    connectable = engine_from_config(
        configuration,
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
""")

# 7. migrations/script.py.mako
create_file("migrations/script.py.mako", """
\"\"\"${message}

Revision ID: ${up_revision}
Revises: ${down_revision | comma,n}
Create Date: ${create_date}

\"\"\"
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
${imports if imports else ""}

# revision identifiers, used by Alembic.
revision: str = ${repr(up_revision)}
down_revision: Union[str, None] = ${repr(down_revision)}
branch_labels: Union[str, Sequence[str], None] = ${repr(branch_labels)}
depends_on: Union[str, Sequence[str], None] = ${repr(depends_on)}

def upgrade() -> None:
    ${upgrades if upgrades else "pass"}

def downgrade() -> None:
    ${downgrades if downgrades else "pass"}
""")

# 8. migrations/versions/.gitkeep
create_file("migrations/versions/.gitkeep", "")

# 9. scripts/bootstrap.sh
create_file("scripts/bootstrap.sh", """
#!/usr/bin/env bash
set -e

echo "Bootstrapping git-graph environment..."

if ! command -v uv &> /dev/null; then
    echo "uv could not be found. Please install it (https://github.com/astral-sh/uv)."
    exit 1
fi

echo "Installing dependencies..."
uv venv
source .venv/bin/activate || source .venv/Scripts/activate
uv pip install -e ".[dev]"

echo "Starting PostgreSQL via docker-compose..."
docker-compose up -d postgres

echo "Waiting for PostgreSQL to be ready..."
until docker-compose exec postgres pg_isready -U postgres -d git_graph_dev; do
  sleep 1
done

echo "Running database migrations..."
alembic upgrade head

echo "Bootstrap complete!"
""")
