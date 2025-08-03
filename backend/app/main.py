from fastapi import FastAPI

from .utils import consts
from .task import task_router

app = FastAPI(
    title="Site Analyzer API",
    description="APIs for Site Analyzer application",
    version="1.0.0"
)

# Include routers
app.include_router(task_router)


@app.get("/")
async def root():
    return {"message": consts.test_content}