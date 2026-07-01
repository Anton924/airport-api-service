# Airport API Service

A RESTful API for managing airports, routes, flights, airplanes, crews and ticket orders.
Built with Django REST Framework and secured with JWT authentication, it gives airlines and travel platforms a structured way to plan flights, assign airplanes and crews, and let users book tickets through orders.

## Installing / Getting started

To get the project up and running on your local machine using Docker:

```
  # Clone the repository
  git clone https://github.com/Anton924/airport-api-service.git
  cd airport-api-service

  # Copy the environment template and fill in your own values
  cp .env.example .env

  # Build and run the containers (app + Postgres)
  docker compose up --build
```

Once the containers are running, the application will be available at: http://localhost:8000/

Note: Most endpoints require authentication (JWT). Register a user via `/api/user/register/` and obtain a token via `/api/user/token/`.

### Without Docker

```
  # Set up virtual environment
  python3 -m venv venv
  source venv/bin/activate

  # Install dependencies
  pip install -r requirements.txt

  # Run migrations and start server
  python3 manage.py migrate
  python3 manage.py runserver
```

By default `manage.py` uses `airport_api_service.settings.dev`, which runs on SQLite — no Postgres required for local development.

## Initial Configuration & Demo Data

You can choose one of the two following ways to start:

### Option 1: Quick Start (With Demo Data)

Use this if you want to see how the system works with pre-filled airports, airplanes, routes, flights and crew members.

1. Seed the database:

```
  python3 manage.py seed_db
```

2. Login with these credentials:

* Admin: `admin@example.com` / `admin12345`
* Regular user: `test@example.com` / `test12345`

### Option 2: Clean Setup

Use this if you want to build your own data from scratch.

1. Create your own administrator:

```
  python3 manage.py createsuperuser
```

2. Log in to the admin panel (`/admin/`) and start creating Airports, Airplane Types, Airplanes, Crew, Routes and Flights.

## Developing

To start developing or adding new features, follow the standard Django workflow. The project structure is organized as follows:

* `airport_api_service/` — Main project configuration (settings split into `base.py`, `dev.py`, `prod.py`, urls, wsgi).
* `airport/` — Core application logic (models, views, serializers, filters, management commands, tests).
* `users/` — Custom user model (email-based authentication), registration and JWT endpoints.

## Testing

The project includes a test suite covering the API endpoints. Before submitting changes, run:

```
  python3 manage.py test
```

Tests are located in `airport/tests/` and cover airports, airplanes, routes, flights and orders, including filtering and validation.

Note: If you want to add your own tests, please put them in a separate file within the `tests/` directory (e.g., `test_new_feature.py`) to maintain the project structure.

## Code Quality

We use `Flake8` for linting. You can check your code style by running:

```
  flake8 .
```

But it can take some time, so it will be easier to check a specific directory. For example:

```
  # Example: Check only the models file
  flake8 airport/models.py

  # Example: Check the project settings
  flake8 airport_api_service/settings/base.py
```

## Building

If you modify the data structure in `airport/models.py` or `users/models.py`, you must update the database schema:

```
  python3 manage.py makemigrations
  python3 manage.py migrate
```

These commands will detect your changes in Python models and create/apply corresponding SQL commands to update the database.

## Deploying / Publishing

This project ships with a `Dockerfile` and is deployed on [Render](https://render.com) using Docker.

1. Set the following environment variables on your hosting provider:
   `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_HOST`, `POSTGRES_DB_PORT`, `SECRET_KEY`, `DJANGO_SETTINGS_MODULE=airport_api_service.settings.prod`

2. On every push to `main`, GitHub Actions runs linting and tests, then triggers a deploy via Render's Deploy Hook if they pass — see `.github/workflows/ci.yml`.

## Features

This API provides a structured approach to airline operations, from route planning to ticket booking.

* **Flight & Route Management**: Define airports, create routes between them with distances, and schedule flights with departure/arrival times.
* **Fleet & Crew Management**: Register airplane types and airplanes with row/seat configuration, and assign crew members to flights.
* **Ticket Ordering**: Authenticated users can place orders containing one or more tickets, with validation to prevent duplicate or invalid seat bookings.
* **Flexible Filtering**: Filter flights by route or departure date, and other list endpoints by relevant fields.
* **JWT Authentication**: Secure access via `djangorestframework-simplejwt`, with token obtain/refresh/verify endpoints and a self-service registration/profile endpoint.
* **Rate Limiting**: Built-in throttling for anonymous and authenticated users to protect the API from abuse.
* **Interactive API Docs**: Auto-generated OpenAPI schema with Swagger UI and Redoc, powered by `drf-spectacular`.
* **Dockerized Deployment**: Production-ready Docker setup with `gunicorn`, health-checked Postgres, and CI/CD via GitHub Actions.

## Configuration

Settings are split into `airport_api_service/settings/base.py`, `dev.py` and `prod.py`, selected via the `DJANGO_SETTINGS_MODULE` environment variable.

### SECRET_KEY
Type: `String` Default: `Django generated.`
Used for security. Always change this for production.

### DEBUG
Type: `Boolean` Default: `True` in `dev`, `False` in `prod`.
Set to `False` in production to hide sensitive error details.

### POSTGRES_DB / POSTGRES_USER / POSTGRES_PASSWORD / POSTGRES_HOST / POSTGRES_DB_PORT
Type: `String` / `Integer`
Required in production (`prod.py`) to connect to the PostgreSQL database. Not used in `dev.py`, which runs on SQLite.

## Contributing

If you'd like to contribute, please fork the repository and use a feature branch. Pull requests are warmly welcome.

## Links

* Project homepage: https://airport-api-service.onrender.com/api/schema/swagger-ui/
* Repository: https://github.com/Anton924/airport-api-service
* Issue tracker: https://github.com/Anton924/airport-api-service/issues
  * In case of sensitive bugs like security vulnerabilities, please contact `yakovenkoanton2007@gmail.com` directly instead of using the issue tracker. I value your effort to improve the security and privacy of this project!

## Licensing

The code in this project is licensed under the MIT License. For the full legal text, please refer to the [LICENSE](https://github.com/Anton924/airport-api-service/blob/main/LICENSE) file located in the root directory of this repository.
