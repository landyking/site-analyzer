from enum import Enum
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, EmailStr


class TaskStatus(int, Enum):
    CREATED = 1
    PROCESSING = 2
    SUCCESS = 3
    FAILURE = 4
    CANCELLED = 5


class ConstraintFactor(BaseModel):
    kind: str
    value: float


class SuitabilityFactorRange(BaseModel):
    start: float
    end: float
    points: int


class SuitabilityFactor(BaseModel):
    kind: str
    weight: float
    ranges: List[SuitabilityFactorRange]


class CreateMapTaskReq(BaseModel):
    name: str
    district_code: str
    constraint_factors: List[ConstraintFactor]
    suitability_factors: List[SuitabilityFactor]


class MapTaskFile(BaseModel):
    id: int
    map_task_id: int
    file_type: str
    file_path: str
    created_at: datetime


class MapTask(BaseModel):
    id: int
    name: str
    user_id: int
    user_email: EmailStr
    district_code: str
    district_name: str
    status: TaskStatus
    started_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None
    created_at: datetime


class MapTaskDetails(MapTask):
    files: Optional[List[MapTaskFile]] = []
    constraint_factors: Optional[List[ConstraintFactor]] = []
    suitability_factors: Optional[List[SuitabilityFactor]] = []


class BaseResp(BaseModel):
    error: int = 0


class MyMapTaskListResp(BaseResp):
    list: List[MapTask] = []


class MyMapTaskResp(BaseResp):
    data: MapTaskDetails
