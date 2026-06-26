# Level 2 — Intermediate & Advanced FastAPI

This directory contains Level 2 exercises and examples for learning intermediate to advanced FastAPI concepts. The goal of Level 2 is to show how a production-like FastAPI service is organized and how requests flow through routers, dependencies, business logic, and persistence layers.

> This README explains the working flow, core components, how to run the code locally, and recommended development practices.

---

## Goals

- Demonstrate how to structure a larger FastAPI application using APIRouters and modular packages.
- Show common production patterns: dependency injection, authentication (JWT/OAuth2), database integration (async or sync), migrations, background tasks, and testing.
- Provide conventions for models (Pydantic schemas), database models (ORM), and service layers.

## High-level architecture & request flow

1. Client sends an HTTP request to an endpoint (e.g. `POST /auth/login`, `GET /items/`).
2. The request is received by FastAPI server and matched to an APIRouter path.
3. Path operation dependencies and global dependencies (authentication, DB session, rate limiting) are resolved.
4. Request body is validated by Pydantic schemas (input models).
5. The router calls an application-level service or controller function that contains business logic.
6. The service uses repository/DAO functions to interact with the database (via an async engine like SQLAlchemy Async or a sync ORM) or external services (Redis, external APIs, message broker).
7. The DB layer executes queries and returns domain models which are converted to Pydantic response schemas.
8. Background tasks (if any) are scheduled, and the response is returned to the client.
9. Event handlers (startup/shutdown) manage resources (DB pools, Redis connections, scheduler services).

Flow diagram (textual):

Client -> FastAPI -> APIRouter -> Dependencies (auth, DB) -> Service/Controller -> Repository/DAO -> Database/External

Background & async tasks: Service -> BackgroundTask / Celery -> Worker -> External systems

---

## Typical project layout (convention)

- app/
  - main.py                 # FastAPI application factory and app instance
  - api/
    - v1/
      - routers/*.py        # APIRouter modules (auth, users, items, etc.)
  - core/
    - config.py             # Settings and environment handling (pydantic BaseSettings)
    - security.py           # JWT helpers, password hashing
  - db/
    - session.py            # DB engine and session management
    - base.py               # Base metadata for models
    - migrations/           # Alembic configs (if present)
  - models/                 # ORM models
  - schemas/                # Pydantic request/response models
  - services/               # Business logic / use-cases
  - repositories/           # DB access logic
  - dependencies.py         # Shared dependency functions (get_db, get_current_user)
  - tasks/                  # Background tasks and Celery integration
  - utils/                  # Helpers, validators, common utilities
  - tests/                  # Unit and integration tests

This layout is flexible but the separation encourages clear responsibilities: routers only handle request/response, services contain business rules, repositories handle persistence.

---

## Key components explained

- APIRouter: registers paths and request validation. Keep routers thin — call services.
- Dependencies: use FastAPI's dependency injection to provide DB sessions, authenticated users, and config.
- Pydantic Schemas: use separate input (Create/Update) and output (Read) schemas to avoid leaking internal fields.
- Services: implement transactional business logic; call repositories and other infra.
- Repositories/DAO: single place to interact with the DB. Encapsulate raw SQL or ORM queries here.
- DB Session management: prefer context-managed sessions injected per-request. For async: use async session with an async DB engine.
- Migrations: use Alembic for schema migrations. Keep migration configs under db/migrations or migrations/.
- Auth & Security: centralize JWT creation, verification, password hashing, token expiry handling. Protect sensitive endpoints with dependencies that verify tokens and scopes/roles.
- Background Jobs: for short-lived background work, use FastAPI's BackgroundTasks; for heavy or long-running jobs, use Celery/RQ and a separate worker process.

---

## Running locally (example)

1. Create a virtual env and install dependencies:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. Copy or set environment variables (example using `.env`):

- DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/dbname
- SECRET_KEY=your_secret_key
- ACCESS_TOKEN_EXPIRE_MINUTES=60

3. Run migrations (if Alembic is configured):

```bash
alembic upgrade head
```

4. Start the app:

```bash
uvicorn app.main:app --reload
```

Open http://127.0.0.1:8000/docs for the interactive API docs.

---

## Development & testing

- Run unit tests:

```bash
pytest -q
```

- Lint and type-check:

```bash
ruff .
mypy app
```

- Use test containers or a local test DB to run integration tests against a real DB rather than mocking everything.

---

## Deployment notes

- Use an ASGI server like Uvicorn or Hypercorn behind a process manager (gunicorn-workers with uvicorn workers) for production.
- Configure environment variables securely (secrets manager or CI secrets).
- Use connection pooling and health checks. Tune pool sizes to your DB and workload.
- Consider separate workers for background jobs (Celery) and a message broker like Redis or RabbitMQ.

---

## Conventions & tips

- Keep routers thin: move business logic into services.
- Validate inputs strictly and return clear error responses using FastAPI's HTTPException and custom exception handlers.
- Use Pydantic models for both validation and documentation.
- Prefer dependency-injection over global singletons for resources that need cleanup.
- Write integration tests for critical flows: auth, database transactions, and error handling.

---

## What to customize for this repo

- Confirm whether the project uses async SQLAlchemy, Tortoise ORM, or a sync ORM — adapt the `db/session.py` and dependency functions accordingly.
- Check for an existing `app/core/config.py` or `.env.example` to document the required environment variables for Level 2.
- If Celery is included, add a `tasks/README.md` explaining worker startup and broker configuration.

---

If you want, I can tailor this README to the exact files and code in Level_2_Intermediate_Advance_FastAPI (list endpoints, show exact run commands, and link to specific files) — tell me if you'd like me to inspect the directory and make the README more specific.
