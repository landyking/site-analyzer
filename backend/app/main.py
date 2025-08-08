from fastapi import FastAPI
from sqlmodel import SQLModel

from app.db import engine
from app import models as _models  # ensure models are imported and tables registered

from app.api.main import api_router
from app.task.routes import router as task_router

app = FastAPI(
    title="Site Analyzer API",
    description="APIs for Site Analyzer application",
    version="1.0.0"
)

# Include routers
# app.include_router(task_router)
app.include_router(api_router)


@app.on_event("startup")
def on_startup() -> None:
    # Ensure tables exist (no-op if already created in MySQL)
    SQLModel.metadata.create_all(engine)