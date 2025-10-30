# URL Shortener API

This is a simple URL shortening service built with FastAPI, SQLAlchemy, PostgreSQL, Docker and Redis.

## Features

*   **URL Shortening:** Converts long URLs into short, unique 7-character codes.
*   **Redirection:** Redirects users from the short URL to the original long URL.
*   **Click Analytics:** Tracks the number of times a short URL has been accessed.
*   **Redis Caching:** Implements a cache-aside strategy with Redis to speed up redirection requests.
*   **Expiration Times:** Supports setting an optional expiration date for short URLs.
*   **API Key Authentication:** Secures the analytics endpoint with an API key.
*   **Database Migrations:** Uses Alembic for managing database schema changes.
*   **Dockerized:** The application services (API, PostgreSQL, Redis) are containerized using Docker Compose.

## Setup Roadmap

Follow these steps to get the project up and running on your local machine.

### Prerequisites

Ensure you have the following installed:

*   **Git:** For cloning the repository.
*   **Docker Desktop:** (or Docker Engine) For running the containerized services.
*   **Python 3.12+:** For virtual environment and local development.
*   **pip:** Python package installer.

### 1. Clone the Repository

```bash
git clone https://github.com/VincentMssx/url-shorten.git
cd url-shorten
```

### 2. Virtual Environment (Optional but Recommended)

```bash
python -m venv venv
# On Windows
.\venv\Scripts\activate
# On macOS/Linux
source venv/bin/activate
```

### 3. Install Dependencies

Install the project's runtime and development dependencies.

```bash
pip install -r requirements.txt
```

### 4. Docker Setup

#### a. Build Docker Images

Build the Docker images for the services defined in `docker-compose.yml`.

```bash
docker-compose build
```

#### b. Start Docker Containers

Start the PostgreSQL database, Redis cache, and FastAPI application services in detached mode.

```bash
docker-compose up -d
```

#### c. Stop Docker Containers

To stop the running containers:

```bash
docker-compose down
```

### 5. Database Migrations (Alembic)

The project uses Alembic for database schema management. This ensure the database structure matches the application's models.

#### a. Generate Initial Migration (First Time Setup or Schema Changes)


```bash
docker-compose exec api alembic revision --autogenerate -m "Initial migration"
```

#### b. Apply Migrations

Apply the pending migrations to the database. **Run this command inside the `api` container:**

```bash
docker-compose exec api alembic upgrade head
```

*(Note: The `CMD` in the Dockerfile already runs `alembic upgrade head` on `api` service startup, so this step is primarily for manual application or in development workflows before starting the API.)*

### 6. Accessing the API

The FastAPI application will be running on `http://localhost:8000`.

#### a. Swagger UI (Interactive API Documentation)

Access the interactive API documentation at: `http://localhost:8000/docs`

**Using API Key on Swagger UI:**

1.  Click the "Authorize" button
2.  Enter your API key (`mysecretapikey` by default) in the `X-API-KEY` field.
3.  Click "Authorize". Subsequent requests from Swagger UI will include the API key.

#### b. API Usage Examples (cURL)

Here are some cURL commands to interact with the API.

*   **Shorten a URL:**
    ```bash
    curl -X 'POST' \
      'http://localhost:8000/shorten' \
      -H 'accept: application/json' \
      -H 'X-API-KEY: mysecretapikey' \
      -H 'Content-Type: application/json' \
      -d '{
      "long_url": "https://github.com/VincentMssx/url-shorten/issues",
      "expires_at": "2025-12-30T08:30:34.504542Z"
    }'
    ```
    (Omit `"expires_at"` if you want to use the default 1-day expiration)

*   **Redirect a Short URL:**
    ```bash
    curl -X 'GET' \
      'http://localhost:8000/{YOUR_SHORT_CODE}' \
      -H 'accept: */*'
    ```

*   **Get Analytics for a Short URL:**
    ```bash
    curl -X 'GET' \
      'http://localhost:8000/analytics/{YOUR_SHORT_CODE}' \
      -H 'accept: application/json' \
      -H 'X-API-KEY: mysecretapikey'
    ```

## Technologies Used

*   **FastAPI:** Web framework for building APIs.
*   **SQLAlchemy:** ORM for interacting with PostgreSQL.
*   **PostgreSQL:** Relational database.
*   **Redis:** In-memory data store for caching.
*   **Alembic:** Database migration tool.
*   **Docker & Docker Compose:** Containerization and orchestration.
*   **Pydantic:** Data validation and settings management.
