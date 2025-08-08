from fastapi import APIRouter

from app.models import (
    CreateMapTaskReq,
    MyMapTaskListResp,
    MyMapTaskResp,
    MapTask,
    MapTaskDetails,
    BaseResp,
)

router = APIRouter(tags=["User"])


@router.get("/user/my-map-tasks", response_model=MyMapTaskListResp, summary="Get user's map tasks")
async def user_get_my_map_tasks(completed: bool | None = None) -> MyMapTaskListResp:
    # Placeholder demo data
    tasks = [
        MapTask(id=1, name="Demo Task", status=3),
    ]
    return MyMapTaskListResp(error=0, list=tasks)


@router.post("/user/my-map-tasks", response_model=MyMapTaskResp, summary="Create a new map task")
async def user_create_map_task(payload: CreateMapTaskReq) -> MyMapTaskResp:
    data = MapTaskDetails(id=1, name=payload.name, district_code=payload.district_code,
                          constraint_factors=payload.constraint_factors,
                          suitability_factors=payload.suitability_factors)
    return MyMapTaskResp(error=0, data=data)


@router.get("/user/my-map-tasks/{taskId}", response_model=MyMapTaskResp, summary="Get user's map tasks")
async def user_get_map_task(taskId: int) -> MyMapTaskResp:
    data = MapTaskDetails(id=taskId, name="Demo Task")
    return MyMapTaskResp(error=0, data=data)


@router.post("/user/my-map-tasks/{taskId}/cancel", response_model=BaseResp, summary="Cancel a map task")
async def user_cancel_map_task(taskId: int):
    return BaseResp(error=0)
