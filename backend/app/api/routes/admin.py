from fastapi import APIRouter, HTTPException

from app import crud
from app.api.deps import CurrentAdminUser, SessionDep
from app.api.routes._mappers import (
    as_aware_utc as _as_aware_utc,
    to_map_task as _to_map_task,
    to_map_task_details as _to_map_task_details,
)
from app.core import storage
from app.models import (
    AdminMapTaskResp,
    AdminUpdateUserStatusRequest,
    BaseResp,
    MapTask4AdminPageData,
    MapTaskProgress,
    MapTaskProgressDB,
    MapTaskProgressListResp,
    User4Admin,
    User4AdminPageData,
)

router = APIRouter(tags=["Admin"])


@router.get("/admin/users", response_model=User4AdminPageData, summary="Get user list for admin")
async def admin_get_user_list(
    session: SessionDep,
    current_user: CurrentAdminUser,
    page_size: int | None = 20,
    current_page: int | None = 1,
    keyword: str | None = None,
    status: int | None = None,
) -> User4AdminPageData:
    # Query DB via CRUD with pagination and filters
    ps = max(1, int(page_size) if page_size else 20)
    cp = max(1, int(current_page) if current_page else 1)
    rows, total, ps, cp = crud.admin_list_users(
        session=session,
        page_size=ps,
        current_page=cp,
        keyword=keyword,
        status=status,
    )
    users = [
        User4Admin(
            id=row.id,
            provider=row.provider,
            sub=row.sub,
            email=row.email,
            role=row.role,
            status=row.status,
            created_at=row.created_at,
            last_login=row.last_login,
        )
        for row in rows
    ]
    return User4AdminPageData(
        error=0,
        list=users,
        total=total,
        current_page=cp,
        page_size=ps,
    )


@router.post("/admin/user-status", response_model=BaseResp, summary="Update user status for admin")
async def admin_update_user_status(
    session: SessionDep,
    current_user: CurrentAdminUser,
    payload: AdminUpdateUserStatusRequest,
) -> BaseResp:
    updated = crud.admin_update_user_status(
        session=session, target_user_id=payload.user_id, status=int(payload.status)
    )
    if not updated:
        raise HTTPException(status_code=404, detail="User not found")
    return BaseResp(error=0)


@router.get(
    "/admin/map-tasks", response_model=MapTask4AdminPageData, summary="Get map tasks for admin"
)
async def admin_get_map_tasks(
    session: SessionDep,
    current_user: CurrentAdminUser,
    page_size: int | None = 20,
    current_page: int | None = 1,
    name: str | None = None,
    user_id: int | None = None,
    status: int | None = None,
) -> MapTask4AdminPageData:
    ps = max(1, int(page_size) if page_size else 20)
    cp = max(1, int(current_page) if current_page else 1)
    rows, total, ps, cp = crud.admin_list_map_tasks(
        session=session,
        page_size=ps,
        current_page=cp,
        name=name,
        user_id=user_id,
        status=status,
    )
    tasks = [_to_map_task(session, row) for row in rows]
    return MapTask4AdminPageData(
        error=0,
        list=tasks,
        total=total,
        current_page=cp,
        page_size=ps,
    )


@router.get(
    "/admin/map-tasks/{taskId}",
    response_model=AdminMapTaskResp,
    summary="Get map task details for admin",
)
async def admin_get_map_task(
    session: SessionDep,
    current_user: CurrentAdminUser,
    taskId: int,
) -> AdminMapTaskResp:
    data = crud.admin_get_map_task(session=session, task_id=taskId)
    if not data:
        raise HTTPException(status_code=404, detail="Task not found")
    details = _to_map_task_details(session, data)
    return AdminMapTaskResp(error=0, data=details)


@router.get(
    "/admin/map-tasks/{taskId}/progress",
    response_model=MapTaskProgressListResp,
    summary="Get progress of a map task for admin",
)
async def admin_get_map_task_progress(
    session: SessionDep, current_user: CurrentAdminUser, taskId: int
):
    rows: list[MapTaskProgressDB] = crud.admin_get_map_task_progress(
        session=session, task_id=taskId
    )
    for row in rows:
        row.created_at = _as_aware_utc(row.created_at)
        row.updated_at = _as_aware_utc(row.updated_at)
    progress_list = [MapTaskProgress.model_validate(row.model_dump()) for row in rows]
    return MapTaskProgressListResp(error=0, list=progress_list)


@router.get(
    "/admin/inputs-initialize",
    response_model=BaseResp,
    summary="Initialize input directory for admin",
)
async def admin_initialize_input_directory(session: SessionDep, current_user: CurrentAdminUser):
    result = storage.initialize_input_dir_from_bucket()
    if result.get("error"):
        raise HTTPException(status_code=500, detail="Failed to initialize input directory")
    return BaseResp(error=0)
