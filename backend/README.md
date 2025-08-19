# Site Analyzer Backend

A FastAPI-based backend service for the site analyzer application.

## Prerequisites

- uv (Python package and project manager)

Tip (macOS): install uv with Homebrew or the official installer.

```bash
brew install uv
# or
curl -Ls https://astral.sh/uv/install.sh | sh
```

## Required environment variables

These must be set for authentication to work. See "Google Sign-In configuration (required)" below for details and examples.

- GOOGLE_CLIENT_ID — Google OAuth client ID
- GOOGLE_CLIENT_SECRET — Google OAuth client secret

### Data directories (required)

Configure absolute paths for where input datasets live and where analysis outputs are written. These are read from the repository-root env files (e.g., `.env.local`).

- INPUT_DATA_DIR — absolute path to your input test/production data directory
- OUTPUT_DATA_DIR — absolute path to your output directory

Examples for local development (macOS):

```
# In the repository root .env.local (not under backend/)
INPUT_DATA_DIR=/Users/you/path/to/site-analyzer/test-data
OUTPUT_DATA_DIR=/Users/you/path/to/site-analyzer/output-data
```

Notes:
- Paths must be absolute. `~` is allowed and will be expanded.
- Relative paths (e.g., `../test-data`) will be rejected at startup.

## Setup and Installation (uv)

### Install dependencies and create the virtual environment

Use uv to resolve `pyproject.toml`/`uv.lock`, create `.venv/`, and install everything:

```bash
uv sync
```

This creates a local `.venv/` and installs all dependencies. You do not need to manually activate the environment when using `uv run`, but you can if you prefer:

```bash
source .venv/bin/activate   # macOS/Linux (optional)
```

## Running the Application

Start the FastAPI development server with uv (no activation required):

```bash
uv run fastapi dev app/main.py
# or
uv run uvicorn app.main:app --reload
```

The API will be available at:
- API: http://localhost:8000
- Interactive API docs: http://localhost:8000/docs
- Alternative API docs: http://localhost:8000/redoc

## Google Sign-In configuration (required)

This service uses Google OAuth. Provide the following environment variables:

- GOOGLE_CLIENT_ID
- GOOGLE_CLIENT_SECRET

Development (git-ignored): create a `.env.local` file at the repository root with:

```
GOOGLE_CLIENT_ID=your-google-oauth-client-id
GOOGLE_CLIENT_SECRET=your-google-oauth-client-secret
# Data directories
INPUT_DATA_DIR=/absolute/path/to/test-data
OUTPUT_DATA_DIR=/absolute/path/to/output-data
```

Production: provide the same variables via `.env.production` (not committed) or your deployment environment's secret manager.

Notes:
- Do not commit secrets. Rotate the client secret if it was ever exposed.
- The backend reads these from the process environment; ensure they are set before starting the server.

## Dependency management with uv

- Install/sync all dependencies (creates/updates `.venv/`):

```bash
uv sync
```

- Add a runtime dependency (updates `pyproject.toml` and `uv.lock`):

```bash
uv add package-name
```

- Add a development-only dependency:

```bash
uv add --dev package-name
```

- Remove a dependency:

```bash
uv remove package-name
```

- Upgrade all locked dependencies to the latest allowed by `pyproject.toml`:

```bash
uv lock --upgrade
uv sync
```

- Show installed packages in the current environment:

```bash
uv tree
```

## Example: Adding a new dependency

```bash
# From backend/
uv add requests

# Commit the updated lockfile and project file
git add pyproject.toml uv.lock
git commit -m "Add requests dependency"
```

## Development

### Project Structure

```
backend/
├── app/
│   └── main.py        # Main FastAPI application
├── pyproject.toml     # Project config + dependencies (managed by uv)
├── uv.lock            # Locked, reproducible dependency set (managed by uv)
├── .venv/             # Virtual environment (created by `uv sync`, git-ignored)
└── README.md          # This file
```

### Environment variables (general)

You can define additional variables as needed (e.g., `DEBUG`, `DATABASE_URL`, etc.). Prefer using `.env.local` for development and a secret manager or `.env.production` for production. Ensure these are available in the process environment when launching the app.

## API Documentation

Once the server is running, you can access the interactive API documentation at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Troubleshooting

### Common Issues

1. Import errors: ensure dependencies are installed with `uv sync` (and try recreating the venv if needed: `rm -rf .venv && uv sync`).
2. Port already in use: change the port by running `uv run uvicorn app.main:app --reload --port 8001`.
3. Permission errors: ensure you have write permissions in the project directory.

### Useful Commands

```bash
# Run with automatic environment handling
uv run uvicorn app.main:app --reload

# Inspect dependency tree (optional)
uv tree

# See Python version used by uv
uv run python -V
```

## Time and time zones (UTC policy)

To avoid time zone bugs, the backend stores and processes all instants in UTC. Keep these rules in mind:

- Always store UTC in the database. Treat database values as UTC unless explicitly documented otherwise.
- Use timezone-aware datetimes in Python when generating or returning values to clients.

Practical guidance
- MySQL
	- We use `DATETIME` columns (see SQLModel models). MySQL `DATETIME` doesn’t store a time zone, so we standardize on UTC.
	- The dev `docker-compose.yml` sets the container time zone to UTC: `TZ: UTC`. MySQL’s default time_zone is `SYSTEM`, so `NOW()` will be UTC in our container.
	- If you run your own MySQL, set the server default to UTC (any one of):
		- my.cnf: `default-time-zone = '+00:00'`
		- SQL: `SET GLOBAL time_zone = '+00:00'` (requires restart for new connections or re-connect)
	- Keep session time zone at UTC as well: `SET time_zone = '+00:00'` (your ORM/connection can run this on connect if needed).
	- Prefer fractional seconds when useful: `DATETIME(6)` for microseconds.
- Python (FastAPI)
	- When generating timestamps, use timezone-aware UTC, e.g. `datetime.now(timezone.utc)`.
	- When reading naive `datetime` from MySQL (which is UTC by convention), attach UTC before returning via the API. The API code already normalizes datetimes to UTC-aware values in responses.
	- Convert between UTC and user-local times only at the UI/reporting edges; do not persist local times unless explicitly required.
- When you truly need a local “wall-clock” time (e.g., business hours), store both: the local `DATETIME(6)` plus an IANA time zone string (e.g., `Pacific/Auckland`).

Notes
- `TIMESTAMP` also stores instants in UTC with automatic conversion, but it’s limited to 1970–2038. We use `DATETIME(6)` for a wider range and explicit UTC handling.
- Audit fields using `NOW()`/`CURRENT_TIMESTAMP` in our UTC-configured environment will be in UTC.
