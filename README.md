# DevCollab

A production-grade developer collaboration API built with Django REST Framework. Covers the full spectrum of backend engineering — JWT auth, WebSockets, async task queues, Redis caching, database optimization, and containerized deployment.


---

## Tech Stack

| Layer | Technology |
|---|---|
| Framework | Django 5.x + Django REST Framework |
| Auth | SimpleJWT + django-allauth (GitHub OAuth) |
| Real-time | Django Channels 4.x + Redis channel layer |
| Task queue | Celery 5.x + Celery Beat |
| Cache | Redis (django-redis) |
| Database | PostgreSQL 16 |
| Testing | pytest-django + factory_boy |
| Container | Docker Compose |
| CI/CD | GitHub Actions |
| API Docs | drf-spectacular (OpenAPI 3) |

---

## Project Structure

```
devcollab/
├── config/
│   ├── settings/
│   │   ├── base.py
│   │   ├── development.py
│   │   └── production.py
│   ├── celery.py
│   ├── asgi.py
│   └── urls.py
├── accounts/         # auth, JWT, OAuth, custom user
├── workspaces/       # workspace + membership management
├── projects/         # projects scoped to workspaces
├── tasks/            # tasks, status transitions, activity log
├── notifications/    # Celery email tasks + daily digest
├── realtime/         # Django Channels consumers + presence
├── core/             # shared permissions, pagination, cache keys, exceptions
└── tests/
```

---

## Features

### Auth & Security
- Email-based custom user model (`AbstractBaseUser`)
- JWT authentication via SimpleJWT (access + refresh tokens)
- Token blacklisting on logout
- GitHub OAuth via django-allauth
- Per-endpoint rate throttling (5/min on auth, 100/min for users)
- Role-based access control: `admin`, `member`, `viewer`

### Workspaces, Projects & Tasks
- Full CRUD with nested routing: `workspaces/{id}/projects/{id}/tasks/`
- Workspace membership with role enforcement
- Task status transitions with validation (`todo → in_progress → done`)
- Activity log on every task change using Django signals + `GenericForeignKey`
- Viewer role is read-only; only admins can add/remove members

### Performance
- `select_related` / `prefetch_related` on all querysets (zero N+1)
- Composite DB indexes on frequently filtered fields
- `annotate()` for task counts and completion stats
- `CursorPagination` on task lists, `PageNumberPagination` on workspaces
- Raw SQL reporting endpoint per workspace

### Caching
- Redis cache backend via django-redis
- Per-user cache keys for workspace and project lists
- Automatic cache invalidation via `post_save` / `post_delete` signals
- Sessions stored in Redis

### Async & Scheduled Jobs
- Task assignment emails via Celery (non-blocking)
- Exponential backoff retry (3 attempts: 2s → 4s → 8s)
- Daily digest email at 8am via Celery Beat
- Hourly overdue task detection job

### Real-time (WebSockets)
- Django Channels with Redis channel layer
- JWT authentication on WebSocket handshake (token as query param)
- Live task updates broadcast to all workspace members on any REST change
- Presence tracking — see who's currently viewing a workspace

---

## Getting Started

### Prerequisites
- Python 3.12+
- PostgreSQL 16
- Redis 7

### Local setup

```bash
git clone https://github.com/yourname/devcollab.git
cd devcollab

python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

cp .env.example .env
# fill in SECRET_KEY, DATABASE_URL, REDIS_URL
```

### `.env` example

```
SECRET_KEY=your-secret-key-here
DEBUG=True
DATABASE_URL=postgres://devcollab:devcollab@localhost:5432/devcollab
REDIS_URL=redis://127.0.0.1:6379/0
EMAIL_HOST=smtp.sendgrid.net
EMAIL_HOST_USER=apikey
EMAIL_HOST_PASSWORD=your-sendgrid-key
```

### Run migrations

```bash
python manage.py migrate
python manage.py createsuperuser
```

### Start services

```bash
# Django (ASGI — required for WebSockets)
daphne config.asgi:application

# Celery worker
celery -A config worker --loglevel=info

# Celery Beat scheduler
celery -A config beat --loglevel=info

# Flower monitoring (optional)
celery -A config flower --port=5555
```

---

## API Overview

### Auth

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/auth/register/` | Register with email + password |
| POST | `/api/auth/login/` | Login, returns access + refresh tokens |
| POST | `/api/auth/logout/` | Blacklist refresh token |
| POST | `/api/auth/token/refresh/` | Refresh access token |
| GET | `/api/auth/me/` | Current user profile |

### Workspaces

| Method | Endpoint | Description |
|---|---|---|
| GET/POST | `/workspaces/` | List / create workspaces |
| GET/PATCH/DELETE | `/workspaces/{id}/` | Retrieve / update / delete |
| POST | `/workspaces/{id}/add-member/` | Add member with role |
| DELETE | `/workspaces/{id}/rem-member/` | Remove member |
| GET | `/workspaces/{id}/report/` | Per-project stats (raw SQL) |

### Projects & Tasks

| Method | Endpoint | Description |
|---|---|---|
| GET/POST | `/workspaces/{id}/projects/` | List / create projects |
| GET/POST | `/workspaces/{id}/projects/{id}/tasks/` | List / create tasks |
| POST | `/workspaces/{id}/projects/{id}/tasks/{id}/change_status/` | Transition task status |
| GET | `/workspaces/{id}/projects/{id}/tasks/{id}/activity/` | Activity log |

### WebSockets

| URL | Description |
|---|---|
| `ws://host/ws/workspaces/{id}/tasks/?token=<jwt>` | Live task updates |
| `ws://host/ws/workspaces/{id}/presence/?token=<jwt>` | Online presence |

---

## Docker

```bash
docker-compose up --build
```

Services started: `web`, `celery`, `beat`, `redis`, `postgres`, `nginx`

The API will be available at `http://localhost:80`.

---

## Testing

```bash
pytest
pytest --cov=. --cov-report=html   # with coverage
```

Test settings use `CELERY_TASK_ALWAYS_EAGER=True` — no worker needed.

---

## Concepts Covered

- Custom `AbstractBaseUser` + `BaseUserManager`
- JWT auth with token rotation and blacklisting
- OAuth2 social login flow (GitHub)
- `ModelViewSet`, nested routers, `@action` decorator
- `SerializerMethodField`, `to_representation`, writable nested serializers
- Django signals (`post_save`, `pre_delete`) + `AppConfig.ready()`
- `GenericForeignKey` / Content Type framework
- N+1 elimination via `select_related` / `prefetch_related`
- `annotate()`, `F()` expressions, composite indexes
- `CursorPagination` vs `PageNumberPagination`
- Redis caching with per-user keys and signal-based invalidation
- Celery task retries with exponential backoff
- Celery Beat periodic scheduling
- ASGI vs WSGI — `ProtocolTypeRouter`
- Django Channels `AsyncJsonWebsocketConsumer`
- JWT middleware for WebSocket handshake
- `async_to_sync` bridging signals → channel layer
- Presence tracking via Redis sets
- Multi-stage Dockerfile + Docker Compose orchestration
- GitHub Actions CI/CD pipeline
