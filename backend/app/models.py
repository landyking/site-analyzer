from __future__ import annotations

import builtins
from datetime import datetime
from enum import IntEnum
from math import isfinite
from typing import Annotated

from pydantic import BaseModel, EmailStr, field_validator, model_validator
from sqlalchemy import BigInteger, Column, DateTime
from sqlalchemy.sql import func
from sqlmodel import Field, SQLModel

# Validation constants from GIS module
from app.gis.consts import (
    ALLOWED_CONSTRAINTS,
    ALLOWED_DISTRICT_CODES,
    ALLOWED_SUITABILITY,
)

# ----------------------
# Base and Pagination
# ----------------------


class BaseResp(BaseModel):
    """Base response model."""

    error: int = 0


class PageData(BaseModel):
    """Pagination base model."""

    total: int | None = None
    current_page: int | None = None
    page_size: int | None = None


# ----------------------
# Common selector Schemas
# ----------------------


class SelectOptionItem(BaseModel):
    """An item in a select dropdown."""

    code: str
    label: str


class SelectOptionListResp(BaseResp):
    """Response model for a list of select options."""

    list: list[SelectOptionItem]


# ----------------------
# District Histogram Schemas
# ----------------------


class DistrictHistogram(BaseModel):
    """A histogram representing district data."""

    frequency: list[int]
    edges: list[float]
    min: float
    max: float


class DistrictHistogramItem(BaseModel):
    """An item in a district histogram."""

    kind: str
    histogram: DistrictHistogram


class DistrictHistogramsResp(BaseResp):
    """Response model for district histograms."""

    list: builtins.list[DistrictHistogramItem] = []


# ----------------------
# Auth Schemas
# ----------------------


class LoginRequest(BaseModel):
    """Request model for user login."""

    email: EmailStr
    password: str


class RegisterRequest(BaseModel):
    """Request model for user registration."""

    email: Annotated[EmailStr, Field(max_length=255)]
    password: Annotated[str, Field(min_length=8, max_length=40)]


class OidcInfoResp(BaseModel):
    """Response model for OIDC provider information."""

    login_url: str


class OidcTokenRequest(BaseModel):
    """Request model for OIDC token exchange."""

    code: str


class LoginResult(BaseModel):
    """Result model for login operations."""

    access_token: str | None = None
    expires_in: int | None = None
    refresh_token: str | None = None
    token_type: str | None = None


class PostLoginResp(BaseResp, LoginResult):
    """Response model after login or registration."""

    pass


# ----------------------
# Map Task Schemas
# ----------------------
class MyMapTaskTileSignature(BaseModel):
    """Signature for a map task tile."""

    exp: int
    task: int
    sig: str


class MyMapTaskTileSignatureResp(BaseResp):
    """Response model for a map task tile signature."""

    data: MyMapTaskTileSignature


class MapTask(BaseModel):
    """Basic information about a map task."""

    id: int
    name: str
    user_id: int
    user_email: EmailStr | None = None
    district_code: str
    district_name: str | None = None
    # status: 1 Created, 2 Processing, 3 Success, 4 Failure, 5 Cancelled
    status: int
    status_desc: str | None = None
    started_at: datetime | None = None
    ended_at: datetime | None = None
    created_at: datetime


class MapTaskFile(BaseModel):
    """Information about a file associated with a map task."""

    id: int
    map_task_id: int
    file_type: str
    file_path: str
    created_at: datetime


class ConstraintFactor(BaseModel):
    """A constraint factor for map tasks."""

    kind: str
    value: float

    @field_validator("kind")
    @classmethod
    def _valid_constraint_kind(cls, v: str) -> str:
        if v not in ALLOWED_CONSTRAINTS:
            raise ValueError(
                f"Invalid constraint kind '{v}'. Allowed: {', '.join(ALLOWED_CONSTRAINTS)}"
            )
        return v

    @field_validator("value")
    @classmethod
    def _non_negative_value(cls, v: float) -> float:
        # allow zero and positive numbers; reject NaN/inf
        if not isfinite(v) or v < 0:
            raise ValueError("value must be a finite number >= 0")
        return v


class SuitabilityFactor(BaseModel):
    """A suitability factor for map tasks."""

    kind: str
    weight: float
    breakpoints: list[float]
    points: list[int]

    @field_validator("kind")
    @classmethod
    def _valid_suitability_kind(cls, v: str) -> str:
        if v not in ALLOWED_SUITABILITY:
            raise ValueError(
                f"Invalid suitability kind '{v}'. Allowed: {', '.join(ALLOWED_SUITABILITY)}"
            )
        return v

    @field_validator("weight")
    @classmethod
    def _valid_weight(cls, v: float) -> float:
        if not isfinite(v) or v <= 0 or v > 10:
            raise ValueError("weight must be in the interval (0, 10]")
        return v

    @model_validator(mode="after")
    def _check_breakpoints_points(self) -> SuitabilityFactor:
        bps = self.breakpoints
        pts = self.points
        if not bps or not pts:
            raise ValueError("breakpoints and points are required")
        if sorted(bps) != bps:
            raise ValueError("breakpoints must be in ascending order")
        if len(pts) != len(bps) + 1:
            raise ValueError("points count must be breakpoints+1")
        if not all(isinstance(p, int) and 0 <= p <= 10 for p in pts):
            raise ValueError("each point must be an integer in [0, 10]")
        if not all(isfinite(bp) for bp in bps):
            raise ValueError("breakpoints must be finite numbers")
        return self


class MapTaskDetails(MapTask):
    """Detailed information about a map task, including files and factors."""

    files: list[MapTaskFile] = []
    constraint_factors: list[ConstraintFactor] = []
    suitability_factors: list[SuitabilityFactor] = []


class MyMapTaskListResp(BaseResp):
    """Response model for a list of map tasks."""

    list: list[MapTaskDetails]


class MyMapTaskResp(BaseResp):
    """Response model for a single map task."""

    data: MapTaskDetails | None = None


class AdminMapTaskResp(BaseResp):
    """Response model for a single map task for admin."""

    data: MapTaskDetails | None = None


class CreateMapTaskReq(BaseModel):
    """Request model for creating a new map task."""

    name: str
    district_code: str
    constraint_factors: list[ConstraintFactor]
    suitability_factors: list[SuitabilityFactor]

    # --- Helpers for factor normalization ---
    @staticmethod
    def _unique_by_kind(items):
        seen = set()
        unique = []
        for it in items:
            k = getattr(it, "kind", None)
            if k is None:
                continue
            if k in seen:
                continue
            seen.add(k)
            unique.append(it)
        return unique

    @staticmethod
    def _order_by_allowed(items, allowed_order: list[str]):
        order = {k: i for i, k in enumerate(allowed_order)}
        return sorted(items, key=lambda it: order.get(getattr(it, "kind", ""), 1_000_000))

    # --- Field validations ---
    @field_validator("district_code")
    @classmethod
    def _valid_district(cls, v: str) -> str:
        if v not in ALLOWED_DISTRICT_CODES:
            raise ValueError("Invalid district_code. Use a valid code from constants.")
        return v

    @field_validator("constraint_factors", mode="after")
    @classmethod
    def _normalize_constraints(cls, v: list[ConstraintFactor]) -> list[ConstraintFactor]:
        if v is None:
            return []
        # de-duplicate by kind, keep first occurrence and stable order aligned to allowed list
        unique = cls._unique_by_kind(v)
        return cls._order_by_allowed(unique, ALLOWED_CONSTRAINTS)

    @field_validator("suitability_factors", mode="after")
    @classmethod
    def _normalize_suitability(cls, v: list[SuitabilityFactor]) -> list[SuitabilityFactor]:
        if not v:
            raise ValueError("At least one suitability factor is required")
        unique = cls._unique_by_kind(v)
        return cls._order_by_allowed(unique, ALLOWED_SUITABILITY)


# ----------------------
# Admin Schemas
# ----------------------


class User4Admin(BaseModel):
    """User information for admin views."""

    id: int | None = None
    provider: str | None = None
    sub: str | None = None
    email: EmailStr | None = None
    # role: 1 ADMIN, 2 USER
    role: int | None = None
    # status: 1 Active, 2 Locked
    status: int | None = None
    created_at: datetime | None = None
    last_login: datetime | None = None


class User4AdminPageData(BaseResp, PageData):
    """Page data for user list in admin views."""

    list: builtins.list[User4Admin] | None = None


class MapTask4AdminPageData(BaseResp, PageData):
    """Page data for map task list in admin views."""

    list: builtins.list[MapTask] | None = None


class AdminUpdateUserStatusRequest(BaseModel):
    """Request model for updating a user's status by admin."""

    user_id: int
    # Enforce allowed values using enum; FastAPI will 422 on invalid
    status: UserStatus


class UserRole(IntEnum):
    """User roles in the system."""

    ADMIN = 1
    USER = 2


class UserStatus(IntEnum):
    """User account statuses."""

    ACTIVE = 1
    LOCKED = 2


class UserBase(SQLModel):
    """Base model for user information."""

    email: str = Field(unique=True, index=True, max_length=255)
    role: int = Field(default=UserRole.USER)
    status: int = Field(default=UserStatus.LOCKED)
    provider: str = Field(index=True, max_length=100)
    sub: str = Field(index=True, max_length=255)


class UserCreate(UserBase):
    """Model for creating a new user."""

    password: str = Field(min_length=8, max_length=40)


class UserPublic(UserBase):
    """Public user information."""

    id: int


class Token(SQLModel):
    """Model for JWT token response."""

    access_token: str
    token_type: str = "bearer"


# Contents of JWT token
class TokenPayload(SQLModel):
    """Payload contained in JWT token."""

    sub: str
    admin: bool = False


# ----------------------
# Progress Schemas
# ----------------------


class MapTaskProgress(BaseModel):
    """Progress update for a map task."""

    id: int
    map_task_id: int
    percent: int
    description: str | None = None
    phase: str | None = None
    error_msg: str | None = None
    created_at: datetime


class MapTaskProgressListResp(BaseResp):
    """Response model for a list of map task progress updates."""

    list: list[MapTaskProgress]


# ----------------------
# SQLModel ORM Tables (MySQL)
# ----------------------


class UserDB(UserBase, table=True):
    """ORM model for t_user"""

    __tablename__ = "t_user"
    id: int | None = Field(
        default=None, sa_column=Column(BigInteger, primary_key=True, autoincrement=True)
    )
    password_hash: str = Field(max_length=255)
    last_login: datetime | None = Field(default=None, sa_column=Column(DateTime))
    created_at: datetime | None = Field(
        default=None, sa_column=Column(DateTime, server_default=func.now())
    )
    updated_at: datetime | None = Field(
        default=None, sa_column=Column(DateTime, server_default=func.now(), onupdate=func.now())
    )


class MapTaskStatus(IntEnum):
    """Statuses for map tasks."""

    # status: 1 Pending, 2 Processing, 3 Success, 4 Failure, 5 Cancelled
    PENDING = 1
    PROCESSING = 2
    SUCCESS = 3
    FAILURE = 4
    CANCELLED = 5


class MapTaskBase(SQLModel):
    """Base model for map task information."""

    user_id: int = Field(sa_type=BigInteger)
    name: str = Field(max_length=150)
    district: str = Field(max_length=10)
    # Stored as JSON string in TEXT column
    constraint_factors: str = Field(default="[]")
    suitability_factors: str = Field(default="[]")


class MapTaskDB(MapTaskBase, table=True):
    """ORM model for t_map_task"""

    __tablename__ = "t_map_task"

    id: int | None = Field(
        default=None, sa_column=Column(BigInteger, primary_key=True, autoincrement=True)
    )
    status: int = Field(default=MapTaskStatus.PENDING)
    error_msg: str | None = Field(default=None, max_length=255)
    started_at: datetime | None = Field(default=None, sa_column=Column(DateTime))
    ended_at: datetime | None = Field(default=None, sa_column=Column(DateTime))
    created_at: datetime | None = Field(
        default=None, sa_column=Column(DateTime, server_default=func.now())
    )
    updated_at: datetime | None = Field(
        default=None, sa_column=Column(DateTime, server_default=func.now(), onupdate=func.now())
    )


class MapTaskFileDB(SQLModel, table=True):
    """ORM model for t_map_task_files"""

    __tablename__ = "t_map_task_files"

    id: int | None = Field(
        default=None, sa_column=Column(BigInteger, primary_key=True, autoincrement=True)
    )
    user_id: int = Field(sa_type=BigInteger)
    map_task_id: int = Field(sa_type=BigInteger)
    file_type: str = Field(max_length=15)
    file_path: str = Field(max_length=255)
    created_at: datetime | None = Field(
        default=None, sa_column=Column(DateTime, server_default=func.now())
    )
    updated_at: datetime | None = Field(
        default=None, sa_column=Column(DateTime, server_default=func.now(), onupdate=func.now())
    )


class MapTaskProgressDB(SQLModel, table=True):
    """ORM model for t_map_task_progress"""

    __tablename__ = "t_map_task_progress"

    id: int | None = Field(
        default=None, sa_column=Column(BigInteger, primary_key=True, autoincrement=True)
    )
    user_id: int = Field(sa_type=BigInteger)
    map_task_id: int = Field(sa_type=BigInteger)
    percent: int = Field(default=0)  # 0-100
    description: str | None = Field(default=None, max_length=255)
    phase: str | None = Field(default=None, max_length=50)
    error_msg: str | None = Field(default=None, max_length=255)
    created_at: datetime | None = Field(
        default=None, sa_column=Column(DateTime, server_default=func.now())
    )
    updated_at: datetime | None = Field(
        default=None, sa_column=Column(DateTime, server_default=func.now(), onupdate=func.now())
    )
