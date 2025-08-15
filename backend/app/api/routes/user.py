from fastapi import APIRouter

from app.models import (
    CreateMapTaskReq,
    MapTaskDB,
    MyMapTaskListResp,
    MyMapTaskResp,
    MapTask,
    MapTaskDetails,
    BaseResp,
)
from app.api.deps import CurrentUser, SessionDep
from app import crud
import json

router = APIRouter(tags=["User"])


@router.get("/user/my-map-tasks", response_model=MyMapTaskListResp, summary="Get user's map tasks")
async def user_get_my_map_tasks(completed: bool | None = None) -> MyMapTaskListResp:
    # Placeholder demo data
    tasks = [
        MapTask(id=1, name="Demo Task", status=3),
    ]
    return MyMapTaskListResp(error=0, list=tasks)


@router.post("/user/my-map-tasks", response_model=MyMapTaskResp, summary="Create a new map task")
async def user_create_map_task(session: SessionDep,current_user: CurrentUser, payload: CreateMapTaskReq) -> MyMapTaskResp:
    data: MapTaskDB = crud.create_map_task(session=session, user_id=current_user.id, payload=payload)
    my_map_task = MapTaskDetails(
        id=data.id,
        name=data.name,
        constraint_factors=json.loads(data.constraint_factors),
        suitability_factors=json.loads(data.suitability_factors),
        user_id=data.user_id,
        # user_email=data.user_email,
        status=data.status,
        started_at=data.started_at,
        ended_at=data.ended_at,
        created_at=data.created_at,
        updated_at=data.updated_at,
        district_code=data.district,
        # district_name=data.district_name,
    )
    return MyMapTaskResp(error=0, data=my_map_task)


@router.get("/user/my-map-tasks/{taskId}", response_model=MyMapTaskResp, summary="Get user's map tasks")
async def user_get_map_task(taskId: int) -> MyMapTaskResp:
    data = MapTaskDetails(id=taskId, name="Demo Task")
    return MyMapTaskResp(error=0, data=data)


@router.post("/user/my-map-tasks/{taskId}/cancel", response_model=BaseResp, summary="Cancel a map task")
async def user_cancel_map_task(taskId: int):
    return BaseResp(error=0)
