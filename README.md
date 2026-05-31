# Temporal Code Knowledge Graph Platform

A production-grade, AI-powered system designed to ingest Git repositories, parse source code into temporal entities, construct a knowledge graph, track code evolution, enrich relationships with semantic metadata, and expose agentic reasoning capabilities over codebases.

---

## Technical Stack

*   **Runtime**: Python 3.12+
*   **API Framework**: FastAPI
*   **Parsing Engine**: Tree-sitter
*   **Databases**: PostgreSQL + pgvector (Adjacency lists & High-dimensional embeddings)
*   **Git Broker**: GitPython
*   **Background Processing**: Celery + Redis
*   **Agent Logic**: LangGraph
*   **Aesthetic & Standard**: Modular Monolith following Domain-Driven Design and Clean Architecture

---

## Quickstart & Local Setup

### 1. Prerequisite Installations
*   Ensure **Python 3.12** is installed.
*   Ensure **Docker** and **Docker Compose** are running on your system.

### 2. Environment Configuration
Create a `.env` file in the root directory:
```bash
ENVIRONMENT=local
DEBUG=true
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/git_graph_dev
REDIS_URL=redis://localhost:6379/0
LLM_PROVIDER=openai
LLM_API_KEY=your-api-key-here
```

### 3. Bootstrap and Run Infrastructure
Initialize local databases, pgvector extensions, and caching endpoints:
```bash
# Spin up PostgreSQL (with pgvector) and Redis
docker-compose -f infrastructure/docker/docker-compose.local.yml up -d
```

Install Poetry dependencies:
```bash
poetry install
```

Compile Tree-sitter grammars:
```bash
poetry run python scripts/setup_treesitter.py
```

### 4. Running Database Migrations
We utilize Alembic to handle schema versions:
```bash
# Run latest database migrations
poetry run alembic upgrade head
```

### 5. Running the Application
```bash
# Run the API server with live reloading
poetry run uvicorn src.main:app --reload --port 8000
```
Open [http://localhost:8000/docs](http://localhost:8000/docs) to view the OpenAPI (Swagger) Documentation.

---

## Architectural Guidelines

This project utilizes **Domain-Driven Design (DDD)** and **Clean Architecture**.

```text
                        ┌─────────────────────────────────────┐
                        │              Interfaces             │
                        │   (FastAPI routes, CLI, Workers)    │
                        └──────────────────┬──────────────────┘
                                           │
                        ┌──────────────────▼──────────────────┐
                        │             Application             │
                        │    (Use Cases, Commands, Queries)   │
                        └──────────────────┬──────────────────┘
                                           │
                        ┌──────────────────▼──────────────────┐
                        │               Domain                │
                        │   (Entities, Value Objects, Events) │
                        └─────────────────────────────────────┘
                                           ▲
                        ┌──────────────────┴──────────────────┐
                        │           Infrastructure            │
                        │      (SQLAlchemy DB, Git, LLM)      │
                        └─────────────────────────────────────┘
```

1.  **Domain**: Never import frameworks or external libraries here. Define repository interfaces here.
2.  **Application**: Coordinate domain models, execute transaction units, and handle business use cases.
3.  **Infrastructure**: Implement repository interfaces, database queries, and external APIs.
4.  **Interface**: Map HTTP, websockets, or queues to Application use cases.

---

## Testing, Linting & Type Safety

### Automated Tests
Run the test suite using `pytest`:
```bash
poetry run pytest
```

### Code Style & Formatting
Format code:
```bash
poetry run black src/ tests/
```

Run code linters:
```bash
poetry run ruff check src/ tests/
```

### Static Type Checks
Validate strict type assertions using `mypy`:
```bash
poetry run mypy src/
```
