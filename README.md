# NimbleTask

Contact management service with full-text search capabilities and automated synchronization from Nimble CRM.

## Features

- **Full-text search** across contacts using PostgreSQL's built-in text search with GIN index
- **Automated sync** from Nimble API (daily via Taskiq scheduler)
- **CSV import** for initial data loading
- **RESTful API** with FastAPI
- **Database migrations** with Alembic
- **Comprehensive tests** (api, unit and integration tests with testcontainers)

## Tech Stack

- **FastAPI** - Modern async web framework
- **PostgreSQL** - Database with full-text search
- **SQLAlchemy 2.0** - Async ORM with raw SQL for search queries
- **Taskiq + RabbitMQ** - Task queue for scheduled contact updates
- **Docker Compose** - Local development environment
- **pytest** - Testing with testcontainers for integration tests

## Setup

### Prerequisites

- Python 3.13+
- Docker and Docker Compose
- uv (Python package manager)

### Installation

1. Clone the repository

2. Start services:
```bash
docker compose up -d
```

3. Install dependencies:
```bash
uv sync
```

4. Configure environment:
```bash
cp src/.env.example src/.env
# Add your Nimble API token to APP_CONFIG__NIMBLE__TOKEN
```

5. Run migrations:
```bash
cd src
alembic upgrade head
```

6. Import initial contacts from CSV:
```bash
cd src
python importer.py
```

## Usage

### Start API server

```bash
cd src
python main.py
```

API will be available at `http://0.0.0.0:8000`

### Start worker for scheduled tasks

```bash
cd src
taskiq worker core:broker --workers 1 -fsd -tp "**/tasks" --no-configure-logging
taskiq scheduler core:scheduler -fsd -tp "**/tasks"
```

The worker will sync contacts from Nimble API daily.

### API Endpoints

**Search contacts:**
```bash
GET /api/v1/contacts/search?q=<search_query>
```

Example:
```bash
curl "http://0.0.0.0:8000/api/v1/contacts/search?q=john"
```

Returns contacts matching the search query across first name, last name, email, and description fields.

## Testing

Install tests deps:
```bash
uv sync --group test
```

Run tests:
```bash
pytest tests
```

Tests include:
- API tests
- Unit tests 
- Integration tests 


## Project Structure

```
src/
├── api/v1/contact/     # API endpoints and schemas
├── core/               # Core configuration, models, database
├── tasks/              # Background tasks (sync from Nimble)
├── importer.py         # CSV import utility
└── main.py             # Application entry point
```

## Database

The `contacts` table uses a GIN index on the concatenated `to_tsvector` for efficient full-text search:

```sql
to_tsvector('english', coalesce(first_name, '') || ' ' || 
                       coalesce(last_name, '') || ' ' || 
                       coalesce(email, '') || ' ' || 
                       coalesce(description, ''))
```

## Implementation Notes

- Used raw SQL functions (`to_tsvector`, `plainto_tsquery`) through SQLAlchemy for full-text search as required
- Batch insert with `ON CONFLICT DO UPDATE` for efficient upsert operations during sync
- Retry logic with exponential backoff for Nimble API requests
- Proper error handling and logging throughout
- Database migrations for schema management