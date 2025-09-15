from fastapi import APIRouter

from app.api.deps import CurrentAdminUser, SessionDep
from app.models import (
    BaseResp,
    User4AdminPageData,
    AdminUpdateUserStatusRequest,
    MapTask4AdminPageData,
    AdminMapTaskResp,
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
    # Stub implementation: return empty list with pagination meta
    return User4AdminPageData(
        error=0,
        list=[],
        total=0,
        current_page=current_page,
        page_size=page_size,
    )


@router.post("/admin/user-status", response_model=BaseResp, summary="Update user status for admin")
async def admin_update_user_status(
    session: SessionDep,
    current_user: CurrentAdminUser,
    payload: AdminUpdateUserStatusRequest,
) -> BaseResp:
    # Stub implementation: no-op
    return BaseResp(error=0)


@router.get("/admin/map-tasks", response_model=MapTask4AdminPageData, summary="Get map tasks for admin")
async def admin_get_map_tasks(
    session: SessionDep,
    current_user: CurrentAdminUser,
    page_size: int | None = 20,
    current_page: int | None = 1,
    name: str | None = None,
    user_id: int | None = None,
    status: int | None = None,
) -> MapTask4AdminPageData:
    # Stub implementation: return empty list with pagination meta
    return MapTask4AdminPageData(
        error=0,
        list=[],
        total=0,
        current_page=current_page,
        page_size=page_size,
    )


@router.get("/admin/map-tasks/{taskId}", response_model=AdminMapTaskResp, summary="Get map task details for admin")
async def admin_get_map_task(
    session: SessionDep,
    current_user: CurrentAdminUser,
    taskId: int,
) -> AdminMapTaskResp:
    # Stub implementation: return empty data
    return AdminMapTaskResp(error=0, data=None)
