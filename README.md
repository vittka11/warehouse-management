# Warehouse Management Service

Warehouse Management Service is ProjectB of the final Django course project.

It is a separate service for the Bookstore application (ProjectA). Bookstore communicates with Warehouse through a REST API using JWT authentication.

## Architecture

```text
Bookstore (ProjectA)
        |
        | REST API + JWT
        v
Warehouse (ProjectB)
        |
        +---- PostgreSQL
        |
        +---- Redis
        |
        +---- Celery
        |
        +---- Gunicorn
        |
        +---- NGINX
```

## Features

- Warehouse stock management
- Book stock reservation and release
- Stock movement history
- REST API with Django REST Framework
- JWT authentication
- Custom User Model
- Groups and permissions
- Class-Based Views
- PostgreSQL
- Redis caching
- Celery background tasks
- English and Ukrainian localization
- Bootstrap UI
- Swagger / OpenAPI documentation
- Docker and Docker Compose
- NGINX
- Gunicorn
- Sentry integration
- Automated tests
- GitHub Actions CI/CD

## API Endpoints

Authentication:

```text
POST /api/token/
POST /api/token/refresh/
```

Warehouse:

```text
GET  /api/stock/
GET  /api/stock/{book_id}/
POST /api/stock/{book_id}/reserve/
POST /api/stock/{book_id}/release/
GET  /api/movements/
```

Swagger documentation:

```text
/api/docs/
```

OpenAPI schema:

```text
/api/schema/
```

## Bookstore Integration

When an order is created in ProjectA:

1. Bookstore requests a JWT access token from Warehouse.
2. Bookstore sends an authenticated request to Warehouse.
3. Warehouse checks available stock.
4. The requested quantity is reserved.
5. A StockMovement record is created.
6. API errors are handled and logged by Bookstore.

```text
Bookstore
    |
    | POST /api/token/
    v
Warehouse
    |
    | JWT token
    v
Bookstore
    |
    | POST /api/stock/{book_id}/reserve/
    v
Warehouse
```

## Running with Docker

Build and start the services:

```bash
docker compose up -d --build
```

Run migrations:

```bash
docker compose exec web python manage.py migrate
```

Create a superuser:

```bash
docker compose exec web python manage.py createsuperuser
```

## Tests

Run all Warehouse tests:

```bash
docker compose exec web python manage.py test inventory
```

Run tests with coverage:

```bash
docker compose exec web coverage run --source=inventory manage.py test inventory
docker compose exec web coverage report
```

Current test coverage:

```text
96%
```

Required minimum coverage:

```text
70%
```

## CI/CD

GitHub Actions automatically:

- installs project dependencies
- starts PostgreSQL
- starts Redis
- applies migrations
- runs automated tests
- checks that coverage is at least 70%
- builds the Docker image

Workflow file:

```text
.github/workflows/ci.yml
```

## Technologies

- Python
- Django
- Django REST Framework
- SimpleJWT
- PostgreSQL
- Redis
- Celery
- Docker
- Docker Compose
- NGINX
- Gunicorn
- drf-spectacular
- Bootstrap
- Sentry
- GitHub Actions

## Projects

### ProjectA — Bookstore

Main application responsible for books, users, shopping cart, orders and payments.

### ProjectB — Warehouse

Independent service responsible for stock, reservations and stock movements.