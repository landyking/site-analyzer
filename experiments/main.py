##
## uvicorn main:app --reload
## uv run uvicorn main:app --reload
##
import os
from typing import Annotated
from fastapi import FastAPI, Query
from titiler.core.factory import TilerFactory, ColorMapFactory

from starlette.middleware.cors import CORSMiddleware

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins (for development - be more specific in production)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create a TilerFactory for Cloud-Optimized GeoTIFFs
cog = TilerFactory()
colormap = ColorMapFactory()

# Register all the COG endpoints automatically
app.include_router(cog.router, tags=["Cloud Optimized GeoTIFF"])
app.include_router(colormap.router, tags=["Cloud Optimized GeoTIFF"])
root_dir = os.path.abspath(f"..")

def DatasetPathParams2(task: Annotated[str, Query(description="task id")], tag: Annotated[str, Query(description="tag")]) -> str:
    """Create dataset path from args"""
    url = f"file://{root_dir}/output-data/{task}/{tag}.tif"
    print(f"Using dataset path: {url}")
    mappings = {
        "final": f"file://{root_dir}/output-data/engine/task-{task}/zone_masked_Auckland.tif",
        "slope": f"file://{root_dir}/output-data/engine/task-{task}/score/score_slope_Auckland.tif",
    }
    return mappings.get(tag, url)

app.dependency_overrides[cog.path_dependency] = DatasetPathParams2

# Optional: Add a welcome message for the root endpoint
@app.get("/")
def read_index():
    return {"message": "Welcome to TiTiler", "root_path": root_dir}