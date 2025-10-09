## TiTiler microservice

A tiny FastAPI app that exposes TiTiler Core as a tile server. It registers:
- COG tiling endpoints under `/titiler`
- Colormap endpoints under `/titiler`

FastAPI’s automatic docs are available at `/docs` and `/redoc`.

### Quick start

Prereqs: Python 3.13+ and [uv](https://github.com/astral-sh/uv).

```bash
# (optional) install dependencies
uv sync

# run the API on port 8123
uv run uvicorn main:app --reload --port 8123
```

Open http://localhost:8123/docs to explore the API.

### Notes

- CORS is open to all origins for development. Restrict `allow_origins` in production.
- `CPL_VSIL_CURL_USE_HEAD=NO` is set to avoid GDAL HEAD requests (useful for GET-only pre‑signed URLs).

### Package

```bash
# Create a distributable package (tar.gz)
uv build
```