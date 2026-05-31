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
