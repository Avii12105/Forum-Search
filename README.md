# ForumSearch

A full-stack, AI-powered federated search engine that aggregates developer discussions, issues, and answers from multiple communities into a single interface.


## Tech Stack

- **Backend:** Python, FastAPI, SQLAlchemy, PostgreSQL, ChromaDB, Redis
- **Frontend:** React, Vite, JavaScript
- **Infrastructure:** Docker, Docker Compose

# Installation

Make sure the following are installed:

- Docker Desktop
- Git

### 1. Clone the repository

```bash
git clone https://github.com/Avii12105/Forum-Search.git
cd forum-search-engine
```

### 2. Build and start all services

```bash
docker compose up -d --build
```

This starts the application services defined in `docker-compose.yml`.

### 3. Run database migrations

Execute the Alembic migrations inside the backend container:

```bash
docker compose exec backend alembic upgrade head
```

### 4. Open the application

Open:

```text
http://localhost:5173
```

## Running Tests

Run the backend test suite with pytest:

```bash
docker compose exec backend pytest -v
```

