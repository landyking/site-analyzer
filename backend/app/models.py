from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, EmailStr


# ----------------------
# Base and Pagination
# ----------------------


class BaseResp(BaseModel):
    error: int = 0


class PageData(BaseModel):
    total: Optional[int] = None
    current_page: Optional[int] = None
    page_size: Optional[int] = None


# ----------------------
# Auth Schemas
# ----------------------


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    password2: str


class OidcInfoResp(BaseModel):
    login_url: str


class OidcTokenRequest(BaseModel):
    code: str


class LoginResult(BaseModel):
    access_token: Optional[str] = None
    expires_in: Optional[int] = None
    refresh_token: Optional[str] = None
    token_type: Optional[str] = None


class PostLoginResp(BaseResp, LoginResult):
    pass


# ----------------------
# Map Task Schemas
# ----------------------


class MapTask(BaseModel):
    id: Optional[int] = None
    name: Optional[str] = None
    user_id: Optional[int] = None
    user_email: Optional[EmailStr] = None
    district_code: Optional[str] = None
    district_name: Optional[str] = None
    # status: 1 Created, 2 Processing, 3 Success, 4 Failure, 5 Cancelled
    status: Optional[int] = None
    started_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None
    created_at: Optional[datetime] = None


class MapTaskFile(BaseModel):
    id: Optional[int] = None
    map_task_id: Optional[int] = None
    file_type: Optional[str] = None
    file_path: Optional[str] = None
    created_at: Optional[datetime] = None


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


class MapTaskDetails(MapTask):
    files: Optional[List[MapTaskFile]] = None
    constraint_factors: Optional[List[ConstraintFactor]] = None
    suitability_factors: Optional[List[SuitabilityFactor]] = None


class MyMapTaskListResp(BaseResp):
    list: Optional[List[MapTask]] = None


class MyMapTaskResp(BaseResp):
    data: Optional[MapTaskDetails] = None


class AdminMapTaskResp(BaseResp):
    data: Optional[MapTaskDetails] = None


class CreateMapTaskReq(BaseModel):
    name: str
    district_code: str
    constraint_factors: List[ConstraintFactor]
    suitability_factors: List[SuitabilityFactor]


# ----------------------
# Admin Schemas
# ----------------------


class User4Admin(BaseModel):
    id: Optional[int] = None
    provider: Optional[str] = None
    sub: Optional[str] = None
    email: Optional[EmailStr] = None
    # role: 1 ADMIN, 2 USER
    role: Optional[int] = None
    # status: 1 Active, 2 Locked
    status: Optional[int] = None
    created_at: Optional[datetime] = None
    last_login: Optional[datetime] = None


class User4AdminPageData(BaseResp, PageData):
    list: Optional[List[User4Admin]] = None


class MapTask4AdminPageData(BaseResp, PageData):
    list: Optional[List[MapTask]] = None


class AdminUpdateUserStatusRequest(BaseModel):
    user_id: int
    status: int
