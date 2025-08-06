from fastapi import APIRouter, Depends, HTTPException, Path, Query
from typing import Optional

from app.task.models import (
    MyMapTaskListResp,
    MyMapTaskResp,
    BaseResp,
    CreateMapTaskReq
)
from app.task.service import (
    get_user_map_tasks,
    get_map_task,
    create_map_task,
    cancel_map_task
)

# In a real application, this would be an actual authentication dependency
async def get_current_user():
    # This is a mock implementation - in a real app, this would verify JWT tokens
    # and extract user information from them
    return {"id": 1, "email": "user@example.com"}

router = APIRouter(prefix="/v1/user", tags=["User"])

@router.get("/my-map-tasks", response_model=MyMapTaskListResp)
async def user_get_my_map_tasks(
    completed: Optional[bool] = Query(None, description="Filter for completed map tasks"),
    current_user = Depends(get_current_user)
):
    """
    Get user's map tasks, optionally filtered by completion status.
    """
    tasks = get_user_map_tasks(current_user["id"], completed)
    return MyMapTaskListResp(list=tasks)

@router.post("/my-map-tasks", response_model=MyMapTaskResp)
async def user_create_map_task(
    req: CreateMapTaskReq,
    current_user = Depends(get_current_user)
):
    """
    Create a new map task.
    """
    task = create_map_task(current_user["id"], current_user["email"], req)
    return MyMapTaskResp(data=task)

@router.get("/my-map-tasks/{task_id}", response_model=MyMapTaskResp)
async def user_get_map_task(
    task_id: int = Path(..., description="The ID of the map task"),
    current_user = Depends(get_current_user)
):
    """
    Get a specific map task by ID.
    """
    task = get_map_task(current_user["id"], task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Map task not found")
    return MyMapTaskResp(data=task)

@router.post("/my-map-tasks/{task_id}/cancel", response_model=BaseResp)
async def user_cancel_map_task(
    task_id: int = Path(..., description="The ID of the map task to cancel"),
    current_user = Depends(get_current_user)
):
    """
    Cancel a map task.
    """
    success = cancel_map_task(current_user["id"], task_id)
    if not success:
        raise HTTPException(status_code=400, detail="Task cannot be cancelled")
    return BaseResp()
