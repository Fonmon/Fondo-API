# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Fondo-API is a Django REST API backend for a fund management system (Fondo Montañez). It manages loans, user profiles, activities, savings accounts, and notifications.

- **Framework**: Django 2.2.27 with Django REST Framework 3.11.2
- **Database**: PostgreSQL (requires `hstore` extension)
- **Task Queue**: Celery 5.2.2 with Redis as broker
- **Cloud**: AWS SES (email), AWS SQS (notifications)
- **Python**: 3.9

## Commands

### Development Setup

```bash
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt

# Start Postgres with Docker
docker run -d --name fondo_db -p 5432:5432 \
  -e POSTGRES_DB=fondodev -e POSTGRES_USER=fondouser -e POSTGRES_PASSWORD=fondo postgres

# Enable hstore extension (required)
docker exec -t fondo_db psql -c "CREATE EXTENSION hstore;" -U fondouser -d fondodev

python manage.py migrate
python manage.py runserver
```

### Running Services

```bash
celery -A api worker -l info          # Celery worker
celery -A api beat -l info            # Celery beat scheduler
celery -A api worker -B -l info       # Worker + scheduler combined
```

### Testing

```bash
# Run all tests
python manage.py test

# Run a single test file
python manage.py test fondo_api.tests.test_loan_views

# Run with coverage
coverage run --branch --source='.' manage.py test
coverage report -m --omit="*env*,*tests*,api/wsgi.py,fondo_api/apps.py,manage.py,*migrations*"
coverage html --omit="*env*,*tests*,api/wsgi.py,fondo_api/apps.py,manage.py,*migrations*"
```

The test settings module (`api.settings.test`) is used automatically when running tests.

## Architecture

### Layer Structure

The app follows a clean **Views → Services → Models** pattern:

- **`fondo_api/views/`** — Thin DRF views that validate input, check permissions, and delegate to services
- **`fondo_api/services/`** — All business logic lives here (loan rate calculation, user activation, email sending, etc.)
- **`fondo_api/models.py`** — All database models in a single file
- **`fondo_api/serializers.py`** — All DRF serializers in a single file
- **`fondo_api/permissions.py`** — Role-based access control via `APIRolePermission`

### Settings

Settings are split by environment in `api/settings/`:
- `base.py` — Shared config (apps, middleware, database, logging)
- `development.py` — `DEBUG=True`, hardcoded `SECRET_KEY`
- `production.py` — `DEBUG=False`, secrets from env vars
- `test.py` — Minimal test config

Default `DJANGO_SETTINGS_MODULE` is `api.settings.development`.

### Authentication & Permissions

**Authentication**: DRF `TokenAuthentication`. Obtain tokens via `POST /api-token-auth/` with `{"username": "<email>", "password": "<password>"}`.

**Roles**: ADMIN(0), PRESIDENT(1), TREASURER(2), MEMBER(3) — stored on `UserProfile.role`.

**Permission enforcement**: `APIRolePermission` in `permissions.py` checks a `list_permissions` dict that maps each endpoint+method to the set of allowed roles. To add permissions for a new endpoint, update that dict.

### Background Tasks

- **`fondo_api/celery/tasks.py`**: `send_notification(message)` — publishes to AWS SQS for Lambda processing
- **`fondo_api/scheduler/`**: Periodic tasks (executer factory pattern) run by Celery beat at 10:00 and 14:00 daily
- `SchedulerTask` model drives which tasks run; supports DAILY, WEEKLY, MONTHLY, YEARLY repeats

### Key Models

| Model | Purpose |
|---|---|
| `UserProfile` | Extends Django User; adds `identification`, `role`, `key` (activation) |
| `UserFinance` | Per-user financial state (contributions, balance, quotas) |
| `Loan` | Loan applications; states: WAITING_APPROVAL, APPROVED, DENIED, PAID_OUT |
| `LoanDetail` | Loan payment schedule entries |
| `Activity` / `ActivityYear` / `ActivityUser` | Fund activities and participation |
| `SavingAccount` | Member savings accounts |
| `NotificationSubscriptions` | Push notification endpoints |
| `SchedulerTask` | Scheduled background task definitions |

### Email Templates

Email templates are in `fondo_api/templates/` and rendered by `MailService`. Template selection uses an enum; templates include: user activation, loan approved/denied, power of attorney approved, password reset.

## Environment Variables

| Variable | Description |
|---|---|
| `POSTGRES_DATABASE` | Database name |
| `POSTGRES_USER` | DB username |
| `POSTGRES_PASSWORD` | DB password |
| `POSTGRES_HOST` | DB hostname |
| `POSTGRES_PORT` | DB port |
| `DJANGO_SECRET_KEY` | Secret key (production) |
| `DEFAULT_FROM_EMAIL` | Sender email address |
| `AWS_REGION` | AWS region (e.g., `us-east-2`) |
| `NOTIFICATIONS_QUEUE_URL` | AWS SQS queue URL |
| `HOST_URL_APP` | Frontend app URL (used in emails) |
| `ALLOWED_HOST_DOMAIN` | Django `ALLOWED_HOSTS` (production) |

## CI/CD

AWS CodeBuild pipeline defined in `buildspec.yml`. It spins up a Docker Postgres container, enables hstore, runs migrations, then runs tests with coverage.
