# nestivo-backend

Modular Python FastAPI backend for a multi-tenant platform.

Requirements
- Python 3.12+
- uv
- Docker and Docker Compose

Setup
- Copy .env.sample to .env and adjust values
- Install dependencies with uv sync

Run
- Local server: uv run uvicorn src.main:app --reload
- Docker: docker-compose up --build

Health
- GET http://localhost:8000/health returns {"status": "ok"}

Alembic
- Create database if needed
- Run migrations: uv run alembic upgrade head

Tests
- Run: uv run pytest

Pre-commit
- Install: uv run pre-commit install
- Run on all files: uv run pre-commit run --all-files
