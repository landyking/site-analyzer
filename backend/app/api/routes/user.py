from datetime import datetime, timedelta

from fastapi import APIRouter, BackgroundTasks, HTTPException

from app import crud
from app.api.deps import CurrentAdminUser, CurrentUser, SessionDep
from app.api.routes._mappers import (
    as_aware_utc as _as_aware_utc,
    to_map_task_details as _to_map_task_details,
)
from app.core.security import gen_tile_signature
from app.gis.consts import constraint_factors, districts
from app.gis.district_histograms import HISTOGRAMS
from app.models import (
    BaseResp,
    CreateMapTaskReq,
    DistrictHistogram,
    DistrictHistogramItem,
    DistrictHistogramsResp,
    MapTask,
    MapTaskDB,
    MapTaskProgress,
    MapTaskProgressDB,
    MapTaskProgressListResp,
    MyMapTaskListResp,
    MyMapTaskResp,
    MyMapTaskTileSignature,
    MyMapTaskTileSignatureResp,
    SelectOptionListResp,
)

router = APIRouter(tags=["User"])


@router.get("/user/my-map-tasks", response_model=MyMapTaskListResp, summary="Get user's map tasks")
async def user_get_my_map_tasks(
    session: SessionDep, current_user: CurrentUser, completed: bool | None = None
) -> MyMapTaskListResp:
    """Get a list of the current user's map tasks, optionally filtering by completion status."""
    db_list = crud.list_map_tasks(session=session, user_id=current_user.id, completed=completed)
    tasks: list[MapTask] = [_to_map_task_details(session, data) for data in db_list]
    return MyMapTaskListResp(error=0, list=tasks)


@router.post("/user/my-map-tasks", response_model=MyMapTaskResp, summary="Create a new map task")
async def user_create_map_task(
    background_tasks: BackgroundTasks,
    session: SessionDep,
    current_user: CurrentUser,
    payload: CreateMapTaskReq,
) -> MyMapTaskResp:
    """Create a new map task for the current user."""
    data: MapTaskDB = crud.create_map_task(
        session=session, user_id=current_user.id, payload=payload, background_tasks=background_tasks
    )
    my_map_task = _to_map_task_details(session, data)
    return MyMapTaskResp(error=0, data=my_map_task)


@router.get(
    "/user/my-map-tasks/{taskId}",
    response_model=MyMapTaskResp,
    summary="Get a user's map task by id",
)
async def user_get_map_task(
    session: SessionDep, current_user: CurrentUser, taskId: int
) -> MyMapTaskResp:
    """Get details of a specific map task belonging to the current user."""
    data: MapTaskDB | None = crud.get_map_task(
        session=session, user_id=current_user.id, task_id=taskId
    )
    if not data:
        raise HTTPException(status_code=404, detail="Task not found")
    my_map_task = _to_map_task_details(session, data)
    return MyMapTaskResp(error=0, data=my_map_task)


@router.delete("/user/my-map-tasks/{taskId}", response_model=BaseResp, summary="Delete a map task")
async def user_delete_map_task(session: SessionDep, current_user: CurrentUser, taskId: int):
    """Delete a specific map task belonging to the current user."""
    try:
        data: MapTaskDB | None = crud.delete_map_task(
            session=session, user_id=current_user.id, task_id=taskId
        )
    except ValueError as e:
        # Trying to delete a running task
        raise HTTPException(status_code=400, detail=str(e))
    if not data:
        raise HTTPException(status_code=404, detail="Task not found")
    return BaseResp(error=0)


@router.post(
    "/user/my-map-tasks/{taskId}/cancel", response_model=BaseResp, summary="Cancel a map task"
)
async def user_cancel_map_task(session: SessionDep, current_user: CurrentUser, taskId: int):
    """Cancel a specific map task belonging to the current user."""
    data: MapTaskDB | None = crud.cancel_map_task(
        session=session, user_id=current_user.id, task_id=taskId
    )
    if not data:
        raise HTTPException(status_code=404, detail="Task not found")
    return BaseResp(error=0)


@router.get(
    "/user/my-map-tasks/{taskId}/tile-signature",
    response_model=MyMapTaskTileSignatureResp,
    summary="Get a map task's tile signature",
)
async def user_get_map_task_tile_signature(
    session: SessionDep, current_user: CurrentUser, taskId: int
):
    """Get a tile signature for accessing map tiles of a specific map task."""
    data: MapTaskDB | None = crud.get_map_task(
        session=session, user_id=current_user.id, task_id=taskId
    )
    if not data:
        raise HTTPException(status_code=404, detail="Task not found")
    # generate 1 hour later timestamp
    exp = int((datetime.now() + timedelta(hours=1)).timestamp())
    # generate tile signature
    sig = gen_tile_signature(current_user.id, taskId, exp)
    return MyMapTaskTileSignatureResp(
        error=0, data=MyMapTaskTileSignature(exp=exp, task=taskId, sig=sig)
    )


@router.post(
    "/user/my-map-tasks/{taskId}/duplicate", response_model=BaseResp, summary="Duplicate a map task"
)
async def user_duplicate_map_task(
    background_tasks: BackgroundTasks,
    session: SessionDep,
    current_user: CurrentAdminUser,
    taskId: int,
):
    """Duplicate a specific map task belonging to the current user."""
    data: MapTaskDB | None = crud.duplicate_map_task(
        session=session, user_id=current_user.id, task_id=taskId, background_tasks=background_tasks
    )
    if not data:
        raise HTTPException(status_code=404, detail="Task not found")
    return BaseResp(error=0)


@router.get(
    "/user/select-options/district",
    response_model=SelectOptionListResp,
    summary="Get district select options",
)
async def user_get_district_select_options(
    session: SessionDep,
    current_user: CurrentUser,
    limit: int | None = 50,
    keyword: str | None = None,
) -> SelectOptionListResp:
    """Get district select options."""
    # Build options from constants; filter by keyword; then apply limit if provided and positive
    items = [{"code": code, "label": name} for code, name in districts]
    if keyword:
        kw = keyword.strip().lower()
        if kw:
            items = [it for it in items if kw in it["label"].lower()]
    if limit is not None and limit > 0:
        items = items[:limit]
    return SelectOptionListResp(error=0, list=items)


@router.get(
    "/user/select-options/constraint-factors",
    response_model=SelectOptionListResp,
    summary="Get constraint factors select options",
)
async def user_get_constraint_factors_select_options(
    session: SessionDep,
    current_user: CurrentUser,
    limit: int | None = 50,
    keyword: str | None = None,
) -> SelectOptionListResp:
    """Get constraint factors select options."""
    # Build options from constants; filter by keyword; then apply limit if provided and positive
    items = [{"code": code, "label": label} for code, label in constraint_factors]
    if keyword:
        kw = keyword.strip().lower()
        if kw:
            items = [it for it in items if kw in it["label"].lower()]
    if limit is not None and limit > 0:
        items = items[:limit]
    return SelectOptionListResp(error=0, list=items)


@router.get(
    "/user/my-map-tasks/{taskId}/progress",
    response_model=MapTaskProgressListResp,
    summary="Get progress of a map task",
)
async def user_get_map_task_progress(session: SessionDep, current_user: CurrentUser, taskId: int):
    """Get the progress history of a specific map task belonging to the current user."""
    rows: list[MapTaskProgressDB] = crud.get_map_task_progress(
        session=session, user_id=current_user.id, task_id=taskId
    )
    for row in rows:
        row.created_at = _as_aware_utc(row.created_at)
        row.updated_at = _as_aware_utc(row.updated_at)
    progress_list = [MapTaskProgress.model_validate(row.model_dump()) for row in rows]
    return MapTaskProgressListResp(error=0, list=progress_list)


@router.get(
    "/user/districts/{districtCode}/histograms",
    response_model=DistrictHistogramsResp,
    summary="Get district input data histograms",
)
async def user_get_district_histograms(
    session: SessionDep,
    current_user: CurrentUser,
    districtCode: str,
    kind: str | None = None,
):
    """Get input data histograms for a specific district, optionally filtering by kind."""
    # Look up histograms for the district
    district_data = HISTOGRAMS.get(districtCode)
    if not district_data:
        raise HTTPException(
            status_code=404, detail="District not found or no histogram data available"
        )

    items = []
    if kind:
        # Only return the specified kind if present
        hist = district_data.get(kind)
        if not hist:
            raise HTTPException(
                status_code=404,
                detail=f"Histogram kind '{kind}' not found for district {districtCode}",
            )
        items.append(DistrictHistogramItem(kind=kind, histogram=DistrictHistogram(**hist)))
    else:
        # Return all available kinds for the district
        for k, hist in district_data.items():
            items.append(DistrictHistogramItem(kind=k, histogram=DistrictHistogram(**hist)))

    return DistrictHistogramsResp(error=0, list=items)
