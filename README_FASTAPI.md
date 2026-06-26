# FastAPI — Basics and Step-by-Step Learning Guide

This document is a concise, practical introduction to FastAPI: what it is, why it matters, how it compares to Flask and Django REST Framework (DRF), which ORMs you can use with it, and a step-by-step learning path with examples you can run locally.

---

## What is FastAPI?

FastAPI is a modern, high-performance web framework for building APIs with Python 3.7+ based on standard Python type hints. It provides automatic interactive API documentation (OpenAPI/Swagger), dependency injection, data validation using Pydantic, and excellent async support.

Key features:
- Fast: built on Starlette (ASGI) and Pydantic for speed.
- Type-driven: request validation and clear documentation from Python type hints.
- Async-first: native async support for concurrency and IO-bound workloads.
- Auto-docs: OpenAPI and interactive UIs (/docs, /redoc) built-in.

Why learn it: it's ideal for building modern microservices, async APIs, ML model serving endpoints, and any service that benefits from fast development and high performance.

---

## How FastAPI fits in the Python web ecosystem (comparison)

- Flask
  - Minimal microframework; synchronous by default.
  - Great for simple apps and learning the basics.
  - You add libraries for validation, auth, and OpenAPI.
  - Pros: extremely flexible and minimal. Cons: you must wire more yourself, fewer built-in happy paths for APIs.

- Django REST Framework (DRF)
  - Designed for Django projects; batteries-included (ORM, admin, auth).
  - Excellent for full-stack apps tightly integrated with Django.
  - Pros: mature ecosystem, admin UI, many features out-of-the-box. Cons: heavier, synchronous unless using Django async features.

- FastAPI
  - Focused on APIs and high-performance async use-cases.
  - More structured than Flask for APIs: request/response models, dependencies, automatic docs.
  - Pros: performance, developer productivity, clear typing. Cons: smaller batteries-included ecosystem than Django, you'll choose ORMs and other stacks.

When to choose:
- Use Flask if you need minimalism or are adding API features to a legacy WSGI app.
- Use DRF when your project is already a Django app and you need the full Django ecosystem.
- Use FastAPI for modern API-first services, async workloads, or when you want automatic OpenAPI docs and type-driven validation.

---

## Which ORM should you use with FastAPI?

FastAPI is ORM-agnostic. Popular choices:

- SQLAlchemy (classic, sync) + SQLModel (by the FastAPI author)
  - SQLAlchemy is the Python standard for relational DBs; mature and flexible.
  - SQLModel (built on SQLAlchemy + Pydantic) provides a simpler, typed model experience that integrates nicely with FastAPI.
  - Good for: production apps, migrations (Alembic), complex queries.

- Async SQLAlchemy (1.4+ with async support)
  - Use when you want async DB access with SQLAlchemy core/ORM.
  - Works well with async FastAPI endpoints.

- Tortoise ORM
  - Async-native ORM with Django-like models.
  - Good for fully async stacks, simpler interface, migrations via aerich.

- GINO
  - Async ORM built for SQLAlchemy core with PostgreSQL focus.

- Prisma (Python client)
  - Type-safe ORM inspired by Prisma in the JS ecosystem.

Which to pick:
- If you want long-term flexibility and production readiness, choose SQLAlchemy (or SQLModel) + Alembic migrations.
- If you want a fully async-friendly ORM and simpler API, consider Tortoise or Prisma.

---

## Quick start: Minimal FastAPI app (0 → running)

1) Create a virtual environment and install:

```bash
python -m venv .venv
source .venv/bin/activate
pip install fastapi uvicorn
```

2) Create app file `app/main.py`:

```python
from fastapi import FastAPI

app = FastAPI()

@app.get('/')
async def root():
    return {"message": "Hello, FastAPI!"}
```

3) Run with Uvicorn (ASGI server):

```bash
uvicorn app.main:app --reload
```

4) Open docs at:
- Swagger UI: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc

5) Try curl:

```bash
curl http://127.0.0.1:8000/
```

---

## Adding request validation and examples (Pydantic)

Pydantic models provide validation and generate schema metadata for docs.

Example `app/main.py` with a POST endpoint:

```python
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class Item(BaseModel):
    name: str
    description: str | None = None
    price: float
    tax: float | None = None

@app.post('/items')
async def create_item(item: Item):
    return {"item": item}
```

Try on docs UI where sample JSON will be auto-generated.

---

## Dependency injection and security basics

FastAPI's Depends lets you declare dependencies (DB sessions, auth checks, config) in a clean way.

Simple example (dependency):

```python
from fastapi import Depends

def get_db():
    db = create_db_session()
    try:
        yield db
    finally:
        db.close()

@app.get('/users')
async def list_users(db=Depends(get_db)):
    return db.query(...)
```

Auth: FastAPI supports OAuth2 flows, JWTs, and cookie-based auth via standard dependencies. Use python-jose or similar to sign/verify tokens.

---

## Example with SQLAlchemy (sync) and FastAPI

1) Install:

```bash
pip install sqlalchemy psycopg2-binary alembic  # or sqlite for testing
```

2) Minimal database setup (`database.py`):

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

SQLALCHEMY_DATABASE_URL = 'sqlite:///./test.db'
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={'check_same_thread': False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
```

3) Example model (`models.py`):

```python
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from database import Base

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
```

4) Use dependency get_db and commit/rollback in endpoints.

Tip: Use Alembic for migrations in production and never rely solely on create_all.

---

## Testing

Use TestClient from FastAPI (requests-like) with pytest:

```python
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_root():
    r = client.get('/')
    assert r.status_code == 200
    assert r.json() == {"message": "Hello, FastAPI!"}
```

For DB tests, use a test database or transactional rollbacks to isolate tests.

---

## Deployment tips

- Use Uvicorn or Hypercorn behind a process manager (systemd, Docker, or Kubernetes). Example in Docker: run `uvicorn app.main:app --host 0.0.0.0 --port 80`.
- Configure environment variables for secrets (SECRET_KEY, DB URL) and use a `.env` or secrets manager.
- Use connection pooling and keep an eye on max connections for your DB.
- For background tasks, use FastAPI BackgroundTasks for light jobs and Celery/RQ for heavy/long-running jobs.

---

## FastAPI vs Flask vs DRF — short table

- Performance: FastAPI > Flask ~ DRF (FastAPI usually faster due to async and Starlette).
- Developer speed: FastAPI (automatic docs + Pydantic) > DRF (batteries included, but more config) > Flask (flexible but more wiring).
- Ecosystem: DRF (Django) > Flask (many small extensions) > FastAPI (growing quickly).
- Use-case: microservices/async API → FastAPI; monolith with admin UI and integrated auth → Django/DRF; tiny/simple apps or prototypes → Flask.

---

## Recommended learning path (step-by-step)

1. Basics (1–2 days)
   - Install FastAPI + Uvicorn, run "Hello world" app, explore /docs.
   - Learn Pydantic models and validation.

2. Intermediate (3–7 days)
   - Build CRUD endpoints with Pydantic and path/query/body parameters.
   - Learn dependencies (get_db pattern) and error handling (HTTPException, status codes).
   - Add authentication: OAuth2 password flow and JWT basics.

3. Databases (3–7 days)
   - Integrate SQLAlchemy or SQLModel; write models and simple queries.
   - Learn migrations with Alembic and run a small migration.
   - Optionally try an async ORM (Tortoise or async SQLAlchemy).

4. Testing & CI (2–4 days)
   - Write pytest tests using TestClient.
   - Add a basic CI workflow (GitHub Actions) to run tests and linters.

5. Production readiness (ongoing)
   - Add logging, monitoring, health checks.
   - Secure secrets and configure CORS, rate limiting.
   - Dockerize and deploy (Docker Compose, Kubernetes).

6. Advanced features
   - Background processing (Celery), websockets, streaming responses, GraphQL integration.

---

## Learning resources

- FastAPI official docs: https://fastapi.tiangolo.com
- SQLModel (by FastAPI author): https://sqlmodel.tiangolo.com
- Pydantic docs: https://pydantic-docs.helpmanual.io
- Tutorials: official FastAPI tutorial, YouTube series, and sample projects on GitHub.

---

If you want, I can:
- Create a starter template in this repository (examples: project layout, requirements.txt, minimal auth + DB wiring).
- Implement a small sample CRUD app with SQLModel and Alembic and commit it as a new directory.

Which would you like me to do next?