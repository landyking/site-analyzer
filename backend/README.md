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
