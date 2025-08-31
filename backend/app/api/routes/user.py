from fastapi import APIRouter, HTTPException, BackgroundTasks

from app.models import (
    CreateMapTaskReq,
    MapTaskDB,
    MapTaskFile,
    MapTaskFileDB,
    MapTaskProgressDB,
    MyMapTaskListResp,
    MyMapTaskResp,
    MapTask,
    MapTaskDetails,
    MapTaskStatus,
    BaseResp,
    MyMapTaskTileSignature,
    MyMapTaskTileSignatureResp,
    SelectOptionListResp,
    MapTaskProgress, MapTaskProgressListResp,
    DistrictHistogram, DistrictHistogramItem, DistrictHistogramsResp
)
from app.api.deps import CurrentAdminUser, CurrentUser, SessionDep
from app import crud
import json
from app.gis.consts import districts, constraint_factors
from datetime import datetime, timedelta, timezone

from app.core.security import gen_tile_signature
from app.core import storage

router = APIRouter(tags=["User"])

# Build a fast lookup for district code -> name
_DISTRICT_CODE_TO_NAME = {code: name for code, name in districts}

# Ensure timezone-aware datetimes (UTC) for consistent ISO output with offset
def _as_aware_utc(dt):
    if dt is None:
        return None
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)

def _to_map_task_details(session: SessionDep, data: MapTaskDB) -> MapTaskDetails:
    """Create a MapTaskDetails from a MapTaskDB row, safely parsing JSON fields."""
    # Fetch user email by user_id; ignore failures gracefully
    user_email: str | None = None
    try:
        user = crud.get_user_by_id(session=session, user_id=data.user_id)
        if user:
            user_email = user.email
    except Exception:
        user_email = None

    district_name = _DISTRICT_CODE_TO_NAME.get(data.district)
    # Translate status to a human-readable description using Enum
    status_desc: str | None = None
    try:
        status_desc = MapTaskStatus(data.status).name.title()
    except Exception:
        status_desc = None

    db_files: list[MapTaskFileDB] = crud.get_files_by_id(session=session, user_id=data.user_id, map_task_id=data.id)
    files: list[MapTaskFile] = [MapTaskFile(**file.model_dump()) for file in db_files]
    for f in files:
        f.file_path = storage.generate_presigned_url(f.file_path)
    return MapTaskDetails(
        id=data.id,
        name=data.name,
        files=files,
        constraint_factors=(
            json.loads(data.constraint_factors)
            if isinstance(data.constraint_factors, str)
            else data.constraint_factors
        ),
        suitability_factors=(
            json.loads(data.suitability_factors)
            if isinstance(data.suitability_factors, str)
            else data.suitability_factors
        ),
        user_id=data.user_id,
        user_email=user_email,
        status=data.status,
        status_desc=status_desc,
        started_at=_as_aware_utc(data.started_at),
        ended_at=_as_aware_utc(data.ended_at),
        created_at=_as_aware_utc(data.created_at),
        updated_at=_as_aware_utc(data.updated_at),
        district_code=data.district,
        district_name=district_name,
    )


@router.get("/user/my-map-tasks", response_model=MyMapTaskListResp, summary="Get user's map tasks")
async def user_get_my_map_tasks(session: SessionDep, current_user: CurrentUser, completed: bool | None = None) -> MyMapTaskListResp:
    db_list = crud.list_map_tasks(session=session, user_id=current_user.id, completed=completed)
    tasks: list[MapTask] = [_to_map_task_details(session, data) for data in db_list]
    return MyMapTaskListResp(error=0, list=tasks)


@router.post("/user/my-map-tasks", response_model=MyMapTaskResp, summary="Create a new map task")
async def user_create_map_task(background_tasks: BackgroundTasks, session: SessionDep, current_user: CurrentUser, payload: CreateMapTaskReq) -> MyMapTaskResp:
    data: MapTaskDB = crud.create_map_task(session=session, user_id=current_user.id, payload=payload, background_tasks=background_tasks)
    my_map_task = _to_map_task_details(session, data)
    return MyMapTaskResp(error=0, data=my_map_task)


@router.get("/user/my-map-tasks/{taskId}", response_model=MyMapTaskResp, summary="Get a user's map task by id")
async def user_get_map_task(session: SessionDep, current_user: CurrentUser, taskId: int) -> MyMapTaskResp:
    data: MapTaskDB | None = crud.get_map_task(session=session, user_id=current_user.id, task_id=taskId)
    if not data:
        raise HTTPException(status_code=404, detail="Task not found")
    my_map_task = _to_map_task_details(session, data)
    return MyMapTaskResp(error=0, data=my_map_task)


@router.delete("/user/my-map-tasks/{taskId}", response_model=BaseResp, summary="Delete a map task")
async def user_delete_map_task(session: SessionDep, current_user: CurrentUser, taskId: int):
    try:
        data: MapTaskDB | None = crud.delete_map_task(session=session, user_id=current_user.id, task_id=taskId)
    except ValueError as e:
        # Trying to delete a running task
        raise HTTPException(status_code=400, detail=str(e))
    if not data:
        raise HTTPException(status_code=404, detail="Task not found")
    return BaseResp(error=0)


@router.post("/user/my-map-tasks/{taskId}/cancel", response_model=BaseResp, summary="Cancel a map task")
async def user_cancel_map_task(session: SessionDep, current_user: CurrentUser, taskId: int):
    data: MapTaskDB | None = crud.cancel_map_task(session=session, user_id=current_user.id, task_id=taskId)
    if not data:
        raise HTTPException(status_code=404, detail="Task not found")
    return BaseResp(error=0)

@router.get("/user/my-map-tasks/{taskId}/tile-signature", response_model=MyMapTaskTileSignatureResp, summary="Get a map task's tile signature")
async def user_get_map_task_tile_signature(session: SessionDep, current_user: CurrentUser, taskId: int):
    data: MapTaskDB | None = crud.get_map_task(session=session, user_id=current_user.id, task_id=taskId)
    if not data:
        raise HTTPException(status_code=404, detail="Task not found")
    # generate 1 hour later timestamp
    exp = int((datetime.now() + timedelta(hours=1)).timestamp())
    sig = gen_tile_signature(current_user.id, taskId, exp)
    return MyMapTaskTileSignatureResp(error=0, data=MyMapTaskTileSignature(exp=exp, task=taskId, sig=sig))


@router.post("/user/my-map-tasks/{taskId}/duplicate", response_model=BaseResp, summary="Duplicate a map task")
async def user_duplicate_map_task(background_tasks: BackgroundTasks, session: SessionDep, current_user: CurrentAdminUser, taskId: int):
    data: MapTaskDB | None = crud.duplicate_map_task(
        session=session, user_id=current_user.id, task_id=taskId, background_tasks=background_tasks
    )
    if not data:
        raise HTTPException(status_code=404, detail="Task not found")
    return BaseResp(error=0)


@router.get("/user/select-options/district", response_model=SelectOptionListResp, summary="Get district select options")
async def user_get_district_select_options(
    session: SessionDep,
    current_user: CurrentUser,
    limit: int | None = 50,
    keyword: str | None = None,
) -> SelectOptionListResp:
    # Build options from constants; filter by keyword; then apply limit if provided and positive
    items = [{"code": code, "label": name} for code, name in districts]
    if keyword:
        kw = keyword.strip().lower()
        if kw:
            items = [it for it in items if kw in it["label"].lower()]
    if limit is not None and limit > 0:
        items = items[:limit]
    return SelectOptionListResp(error=0, list=items)

@router.get("/user/select-options/constraint-factors", response_model=SelectOptionListResp, summary="Get constraint factors select options")
async def user_get_constraint_factors_select_options(
    session: SessionDep,
    current_user: CurrentUser,
    limit: int | None = 50,
    keyword: str | None = None,
) -> SelectOptionListResp:
    # Build options from constants; filter by keyword; then apply limit if provided and positive
    items = [{"code": code, "label": label} for code, label in constraint_factors]
    if keyword:
        kw = keyword.strip().lower()
        if kw:
            items = [it for it in items if kw in it["label"].lower()]
    if limit is not None and limit > 0:
        items = items[:limit]
    return SelectOptionListResp(error=0, list=items)

@router.get("/user/my-map-tasks/{taskId}/progress", response_model=MapTaskProgressListResp, summary="Get progress of a map task")
async def user_get_map_task_progress(session: SessionDep, current_user: CurrentUser, taskId: int):
    rows: list[MapTaskProgressDB] = crud.get_map_task_progress(session=session, user_id=current_user.id, task_id=taskId)
    for row in rows:
        row.created_at = _as_aware_utc(row.created_at)
        row.updated_at = _as_aware_utc(row.updated_at)
    progress_list = [MapTaskProgress.model_validate(row.model_dump()) for row in rows]
    return MapTaskProgressListResp(error=0, list=progress_list)

@router.get("/user/districts/{districtCode}/histograms", response_model=DistrictHistogramsResp, summary="Get district input data histograms")
async def user_get_district_histograms(
    session: SessionDep,
    current_user: CurrentUser,
    districtCode: str,
    kind: str | None = None,
):
    # Implementation will be added later
    pass