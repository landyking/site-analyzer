from datetime import datetime
from typing import Annotated
from fastapi import APIRouter, FastAPI, HTTPException, Query
from app.utils import consts
from titiler.core.factory import TilerFactory, ColorMapFactory

from app.api.deps import CurrentUser, SessionDep
from app import crud
from app.models import MapTaskFileDB
from app.core.security import gen_tile_signature


# Create a TilerFactory for Cloud-Optimized GeoTIFFs
cog = TilerFactory()
colormap = ColorMapFactory()

router = APIRouter(prefix="/titiler")

router.include_router(cog.router, tags=["Cloud Optimized GeoTIFF"])
router.include_router(colormap.router, tags=["Color Map"])

def DatasetPathParams2(session: SessionDep, url: Annotated[str, Query(description="dataset URL")], 
                       exp: Annotated[int, Query(description="Expiration time in seconds")], 
                       sig: Annotated[str, Query(description="Signature")]) -> str:
    """Create dataset path from args"""
    # Extract task and tag from the URL. format: {task}-{tag}
    task, tag = url.split("-")
    file: MapTaskFileDB | None = crud.get_file_by_conditions(session=session, map_task_id=int(task), file_type=tag)
    if not file:
        raise HTTPException(status_code=404, detail="File not found")
    hash: str = gen_tile_signature(file.user_id, file.map_task_id, exp)
    if sig != hash:
        raise HTTPException(status_code=403, detail="Invalid signature")
    if int(datetime.now().timestamp()) > exp:
        raise HTTPException(status_code=403, detail="Expired signature")
    return f"file://{file.file_path}"

def customize_application(app: FastAPI) -> None:
    app.dependency_overrides[cog.path_dependency] = DatasetPathParams2