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
from app.gis.district_histograms import HISTOGRAMS
from datetime import datetime, timedelta, timezone

from app.core.security import gen_tile_signature
from app.core import storage
from app.api.routes._mappers import to_map_task_details as _to_map_task_details
from app.api.routes._mappers import as_aware_utc as _as_aware_utc

router = APIRouter(tags=["User"])

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
    # Look up histograms for the district
    district_data = HISTOGRAMS.get(districtCode)
    if not district_data:
        raise HTTPException(status_code=404, detail="District not found or no histogram data available")

    items = []
    if kind:
        # Only return the specified kind if present
        hist = district_data.get(kind)
        if not hist:
            raise HTTPException(status_code=404, detail=f"Histogram kind '{kind}' not found for district {districtCode}")
        items.append(DistrictHistogramItem(kind=kind, histogram=DistrictHistogram(**hist)))
    else:
        # Return all available kinds for the district
        for k, hist in district_data.items():
            items.append(DistrictHistogramItem(kind=k, histogram=DistrictHistogram(**hist)))

    return DistrictHistogramsResp(error=0, list=items)