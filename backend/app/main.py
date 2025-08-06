from fastapi import FastAPI

from app.api.main import api_router
from app.task.routes import router as task_router

app = FastAPI(
    title="Site Analyzer API",
    description="APIs for Site Analyzer application",
    version="1.0.0"
)

# Include routers
app.include_router(task_router)
app.include_router(api_router)