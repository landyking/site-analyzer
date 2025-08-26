from typing import Annotated
from fastapi import APIRouter, FastAPI, HTTPException, Query
from app.utils import consts
from titiler.core.factory import TilerFactory, ColorMapFactory

from app.api.deps import CurrentUser, SessionDep
from app import crud
from app.models import MapTaskFileDB


# Create a TilerFactory for Cloud-Optimized GeoTIFFs
cog = TilerFactory()
colormap = ColorMapFactory()

router = APIRouter(prefix="/titiler")

router.include_router(cog.router, tags=["Cloud Optimized GeoTIFF"])
router.include_router(colormap.router, tags=["Color Map"])

def DatasetPathParams2(session: SessionDep, current_user: CurrentUser, task: Annotated[int, Query(description="task id")], tag: Annotated[str, Query(description="tag")]) -> str:
    """Create dataset path from args"""
    file: MapTaskFileDB | None = crud.get_file_by_conditions(session, current_user.id, task, tag)
    if not file:
        raise HTTPException(status_code=404, detail="File not found")
    return f"file://{file.path}"

def customize_application(app: FastAPI) -> None:
    app.dependency_overrides[cog.path_dependency] = DatasetPathParams2