from fastapi import APIRouter

from app.models import (
    AdminMapTaskResp,
    MapTask4AdminPageData,
    User4AdminPageData,
    AdminUpdateUserStatusRequest,
    MapTask,
    User4Admin,
    BaseResp,
)

router = APIRouter( tags=["Admin"])


@router.get("/admin/users", response_model=User4AdminPageData, summary="Get user list for admin")
async def admin_get_user_list(
    page_size: int = 20,
    current_page: int = 1,
    keyword: str | None = None,
    status: int | None = None,
) -> User4AdminPageData:
    users = [User4Admin(id=1, email="demo@example.com", role=2, status=1)]
    return User4AdminPageData(error=0, total=1, current_page=current_page, page_size=page_size, list=users)


@router.post("/admin/user-status", response_model=BaseResp, summary="Update user status for admin")
async def admin_update_user_status(payload: AdminUpdateUserStatusRequest):
    return BaseResp(error=0)


@router.get("/admin/map-tasks", response_model=MapTask4AdminPageData, summary="Get map tasks for admin")
async def admin_get_map_tasks(
    page_size: int = 20,
    current_page: int = 1,
    name: str | None = None,
    user_id: int | None = None,
    status: int | None = None,
) -> MapTask4AdminPageData:
    tasks = [MapTask(id=1, name="Demo Task", status=3)]
    return MapTask4AdminPageData(error=0, total=1, current_page=current_page, page_size=page_size, list=tasks)


@router.get("/admin/map-tasks/{taskId}", response_model=AdminMapTaskResp, summary="Get map task details for admin")
async def admin_get_map_task(taskId: int) -> AdminMapTaskResp:
    return AdminMapTaskResp(error=0, data=None)
