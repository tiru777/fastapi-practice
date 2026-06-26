# Level 2 — Intermediate & Advanced FastAPI

This README is tailored to the Level_2_Intermediate_Advance_FastAPI package in this repository. It explains the working flow and the concrete endpoints, models, and run instructions for the code present in this directory.

---

## Quick summary

- Purpose: intermediate/advanced FastAPI learning exercises demonstrating routers, dependencies, simple auth (JWT in cookie), database models (SQLAlchemy), and CRUD operations for users and todos.
- DB: SQLite by default (file: `todo.db`) configured in repository `database.py`.
- Main app entrypoint: `main.py` — routers in this package are included by `main.py`.
- API docs: http://127.0.0.1:8000/docs when running locally.

---

## Files in this package (what they do)

- auth_api.py — authentication endpoints, JWT creation/validation, create user, login (sets auth token in an HTTP-only cookie).
- users.py — user-related endpoints (get current user details, list all users, update password).
- todo.py — todo CRUD endpoints (create, read per-id, read per-user, update, delete).
- admin.py — admin-only endpoints to list all todos and delete any todo (authorization based on `role` claim in token).

Other repository files used by this package:
- models.py — SQLAlchemy models (User, Todo).
- database.py — SQLAlchemy engine/session and Base.
- main.py — FastAPI app factory and router registration.

---

## Data models (DB schema)

From models.py:

- User (table: `user`)
  - id (int, PK)
  - email (str, unique)
  - username (str, unique)
  - firstname (str)
  - lastname (str)
  - hashed_password (str)
  - is_active (bool)
  - role (str) — e.g., `admin` or `user`

- Todo (table: `todo`)
  - id (int, PK)
  - title (str)
  - description (str)
  - priority (str)
  - check (bool)
  - owner_id (int, FK -> user.id)

The SQLite DB file `todo.db` is created automatically when the app first runs (SQLAlchemy create_all is used in the modules).

---

## Endpoints (Level 2 package)

Authentication (auth_api.py)
- POST /auth/user-creation
  - Create a new user.
  - Request body JSON matching CreateUser model:
    - email, username, firstname, lastname, hashed_password (plain password is hashed by code), is_active (bool), role
  - Returns 201 on success.

- POST /auth/token/user-validation
  - Login endpoint using OAuth2 password form (application/x-www-form-urlencoded). Accepts `username` and `password` form fields.
  - On success: sets an HTTP-only cookie named `token` and returns JSON {"token": "<JWT>"}.
  - Token contains claims: sub (username), id (user id), role (user role), exp.

User endpoints (users.py)
- GET /user/get
  - Returns current logged-in user details. Requires auth cookie.
- GET /user/get-users
  - Returns list of all users (no auth required in code; be careful about exposing user lists in production).
- PUT /user/update/{new_password}/{old_password}
  - Update current user's password (verifies old password, then sets new hashed password). Requires auth cookie.

Todo endpoints (todo.py)
- GET /todo/get/{todo_id}
  - Returns todo items with the given id owned by current user. Requires auth cookie.
- GET /todo/get/user/
  - Returns todos for current user. Requires auth cookie.
- POST /todo/post
  - Create a todo for current user. Body JSON matches TodoRequest: title (str), description (str, optional), priority (str), check (bool).
  - Requires auth cookie.
- PUT /todo/update/{todo_id}
  - Update a todo owned by current user. Body JSON same as TodoRequest. Requires auth cookie.
- DELETE /todo/delete/{todo_id}
  - Delete a todo owned by current user. Requires auth cookie.

Admin endpoints (admin.py)
- GET /admin/get
  - Returns all todos. Requires auth cookie and role == "admin".
- DELETE /admin/user/{todo_id}
  - Delete a todo by id (admin-only). Requires auth cookie and role == "admin".

---

## How authentication works in this package

- A JWT token is created in auth_api.create_access_token and signed with a hard-coded SECURITY_KEY in `auth_api.py`.
- The login endpoint stores the JWT in an HTTP-only cookie named `token` and also returns the token in JSON.
- The dependency `get_current_user` reads the cookie `token`, decodes the JWT, and returns a dict: {"user_name", "user_id", "user_role"}.
- Routes call `Depends(get_current_user)` to receive the current user; if the cookie is absent or invalid, many handlers return a 401.

Security notes: the key is hard-coded in the example code — for production use, move this to environment variables and secure secret storage.

---

## Run locally (concrete steps)

1. Create and activate a virtualenv, then install dependencies. If `requirements.txt` is not present, install at least:

```bash
python -m venv .venv
source .venv/bin/activate
pip install fastapi uvicorn sqlalchemy pydantic passlib[bcrypt] python-jose
```

2. Start the app from repository root:

```bash
uvicorn main:app --reload
```

3. Open the interactive docs at:

http://127.0.0.1:8000/docs

4. The first run will create `todo.db` in the repository root (SQLite) because SQLAlchemy create_all is called.

---

## Example usage (curl)

1) Create a user (store plain password in `hashed_password` field — the code hashes it again; in this example we pass a plain password string as `hashed_password`):

```bash
curl -X POST "http://127.0.0.1:8000/auth/user-creation" \
  -H "Content-Type: application/json" \
  -d '{"email":"alice@example.com","username":"alice","firstname":"Alice","lastname":"Example","hashed_password":"mysecret","is_active":true,"role":"user"}'
```

2) Login (obtain token and cookie):

```bash
curl -X POST "http://127.0.0.1:8000/auth/token/user-validation" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=alice&password=mysecret" \
  -c cookies.txt
```

This stores the `token` cookie in `cookies.txt`. The response body also includes the token in JSON.

3) Create a todo using the stored cookie:

```bash
curl -X POST "http://127.0.0.1:8000/todo/post" \
  -H "Content-Type: application/json" \
  -d '{"title":"Buy milk","description":"2 liters","priority":"1","check":false}' \
  -b cookies.txt
```

4) Get current user details:

```bash
curl -X GET "http://127.0.0.1:8000/user/get" -b cookies.txt
```

5) Admin example (assumes a user with role `admin` exists and you logged in as that user):

```bash
curl -X GET "http://127.0.0.1:8000/admin/get" -b cookies.txt
```

---

## Notes, limitations, and suggested improvements

- Password handling: The `user-creation` endpoint expects a `hashed_password` field in the payload but the code hashes it again. In real apps, accept a `password` field and hash it on the server. Avoid storing plaintext anywhere.
- Token storage: Cookies are used here for convenience, but consider CSRF protections, SameSite, secure flags, and proper session handling.
- Secret management: Move SECURITY_KEY and other secrets to environment variables.
- Authorization: Many endpoints check role by reading `user_role` claim — consider adding decorators or reusable dependency functions to centralize role checks.
- Error handling: The code often returns HTTPException instances directly; prefer raising HTTPException for correct FastAPI behaviour.
- Input validation: Some endpoints return raw ORM objects. Use Pydantic response models to avoid leaking internal fields.
- Concurrency/DB sessions: The code uses a synchronous SQLAlchemy session with SQLite. For async workloads or production DBs, consider using async engines and proper pooling.

---

If you want, I can update the code to:
- Add Pydantic request/response schemas and response_model on endpoints.
- Replace the hard-coded SECURITY_KEY with BaseSettings (.env support).
- Add tests for the authentication and todo flows.

Tell me which change you'd like next and I'll make the changes and open a new commit for you.
