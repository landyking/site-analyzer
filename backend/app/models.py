from __future__ import annotations

from datetime import datetime
from typing import List, Optional, Annotated

from pydantic import BaseModel, EmailStr, field_validator, model_validator
from sqlmodel import Field, Relationship, SQLModel
from sqlalchemy import Column, DateTime, Index, BigInteger
from sqlalchemy.sql import func
from enum import Enum, IntEnum
from math import isfinite

# Validation constants from GIS module
from app.gis.consts import (
    ALLOWED_CONSTRAINTS,
    ALLOWED_SUITABILITY,
    ALLOWED_DISTRICT_CODES,
)


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
# Common selector Schemas
# ----------------------


class SelectOptionItem(BaseModel):
    code: str
    label: str


class SelectOptionListResp(BaseResp):
    list: List[SelectOptionItem]


# ----------------------
# Auth Schemas
# ----------------------


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class RegisterRequest(BaseModel):
    email: Annotated[EmailStr, Field(max_length=255)]
    password: Annotated[str, Field(min_length=8, max_length=40)]


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
    id: int
    name: str
    user_id: int
    user_email: EmailStr | None = None
    district_code: str
    district_name: str | None = None
    # status: 1 Created, 2 Processing, 3 Success, 4 Failure, 5 Cancelled
    status: int
    status_desc: str | None = None
    started_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None
    created_at: datetime


class MapTaskFile(BaseModel):
    id: int
    map_task_id: int
    file_type: str
    file_path: str
    created_at: datetime


class ConstraintFactor(BaseModel):
    kind: str
    value: float

    @field_validator("kind")
    @classmethod
    def _valid_constraint_kind(cls, v: str) -> str:
        if v not in ALLOWED_CONSTRAINTS:
            raise ValueError(f"Invalid constraint kind '{v}'. Allowed: {', '.join(ALLOWED_CONSTRAINTS)}")
        return v

    @field_validator("value")
    @classmethod
    def _non_negative_value(cls, v: float) -> float:
        # allow zero and positive numbers; reject NaN/inf
        if not isfinite(v) or v < 0:
            raise ValueError("value must be a finite number >= 0")
        return v


class SuitabilityFactorRange(BaseModel):
    start: float
    end: float
    points: int

    @model_validator(mode="after")
    def _check_range(self) -> "SuitabilityFactorRange":
        if not all(map(isfinite, (self.start, self.end))):
            raise ValueError("range start/end must be finite numbers")
        if self.start >= self.end:
            raise ValueError("range start must be < end")
        if self.points is None or self.points < 1:
            raise ValueError("range points must be >= 1")
        return self


class SuitabilityFactor(BaseModel):
    kind: str
    weight: float
    ranges: List[SuitabilityFactorRange]

    @field_validator("kind")
    @classmethod
    def _valid_suitability_kind(cls, v: str) -> str:
        if v not in ALLOWED_SUITABILITY:
            raise ValueError(f"Invalid suitability kind '{v}'. Allowed: {', '.join(ALLOWED_SUITABILITY)}")
        return v

    @field_validator("weight")
    @classmethod
    def _valid_weight(cls, v: float) -> float:
        if not isfinite(v) or v <= 0 or v > 10:
            raise ValueError("weight must be in the interval (0, 10]")
        return v


class MapTaskDetails(MapTask):
    files: List[MapTaskFile] = []
    constraint_factors: List[ConstraintFactor] = []
    suitability_factors: List[SuitabilityFactor] = []


class MyMapTaskListResp(BaseResp):
    list: List[MapTaskDetails]


class MyMapTaskResp(BaseResp):
    data: Optional[MapTaskDetails] = None


class AdminMapTaskResp(BaseResp):
    data: Optional[MapTaskDetails] = None


class CreateMapTaskReq(BaseModel):
    name: str
    district_code: str
    constraint_factors: List[ConstraintFactor]
    suitability_factors: List[SuitabilityFactor]

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
    def _normalize_constraints(cls, v: List[ConstraintFactor]) -> List[ConstraintFactor]:
        if v is None:
            return []
        # de-duplicate by kind, keep first occurrence and stable order aligned to allowed list
        unique = cls._unique_by_kind(v)
        return cls._order_by_allowed(unique, ALLOWED_CONSTRAINTS)

    @field_validator("suitability_factors", mode="after")
    @classmethod
    def _normalize_suitability(cls, v: List[SuitabilityFactor]) -> List[SuitabilityFactor]:
        if not v:
            raise ValueError("At least one suitability factor is required")
        unique = cls._unique_by_kind(v)
        return cls._order_by_allowed(unique, ALLOWED_SUITABILITY)


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

class UserRole(IntEnum):
    ADMIN = 1
    USER = 2

class UserStatus(IntEnum):
    ACTIVE = 1
    LOCKED = 2
    
class UserBase(SQLModel):
    email: str = Field(unique=True, index=True, max_length=255) 
    role: int = Field(default=UserRole.USER)
    status: int = Field(default=UserStatus.ACTIVE)
    provider: str = Field(index=True, max_length=100)
    sub: str = Field(index=True, max_length=255)

class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=40)

class UserPublic(UserBase):
    id: int

class Token(SQLModel):
    access_token: str
    token_type: str = "bearer"


# Contents of JWT token
class TokenPayload(SQLModel):
    sub: str
    admin: bool = False

# ----------------------
# Progress Schemas
# ----------------------


class MapTaskProgress(BaseModel):
    id: int
    map_task_id: int
    percent: int
    description: str | None = None
    phase: str | None = None
    error_msg: str | None = None
    created_at: datetime

class MapTaskProgressListResp(BaseResp):
    list: List[MapTaskProgress]

# ----------------------
# SQLModel ORM Tables (MySQL)
# ----------------------


class UserDB(UserBase, table=True):
    """ORM model for t_user"""
    __tablename__ = "t_user"
    id: int | None = Field(default=None, sa_column=Column(BigInteger, primary_key=True, autoincrement=True))
    password_hash: str = Field(max_length=255)
    last_login: datetime | None = Field(default=None, sa_column=Column(DateTime))
    created_at: datetime | None = Field(default=None, sa_column=Column(DateTime, server_default=func.now()))
    updated_at: datetime | None = Field(default=None, sa_column=Column(DateTime, server_default=func.now(), onupdate=func.now()))

class MapTaskStatus(IntEnum):
    # status: 1 Pending, 2 Processing, 3 Success, 4 Failure, 5 Cancelled
    PENDING = 1
    PROCESSING = 2
    SUCCESS = 3
    FAILURE = 4
    CANCELLED = 5


class MapTaskBase(SQLModel):
    user_id: int = Field(sa_type=BigInteger)
    name: str = Field(max_length=150)
    district: str = Field(max_length=10)
    # Stored as JSON string in TEXT column
    constraint_factors: str = Field(default="[]")
    suitability_factors: str = Field(default="[]")
    
class MapTaskDB(MapTaskBase, table=True):
    """ORM model for t_map_task"""

    __tablename__ = "t_map_task"

    id: int | None = Field(default=None, sa_column=Column(BigInteger, primary_key=True, autoincrement=True))
    status: int = Field(default=MapTaskStatus.PENDING)
    error_msg: str | None = Field(default=None, max_length=255)
    started_at: datetime | None = Field(default=None, sa_column=Column(DateTime))
    ended_at: datetime | None = Field(default=None, sa_column=Column(DateTime))
    created_at: datetime | None = Field(default=None, sa_column=Column(DateTime, server_default=func.now()))
    updated_at: datetime | None = Field(default=None, sa_column=Column(DateTime, server_default=func.now(), onupdate=func.now()))


class MapTaskFileDB(SQLModel, table=True):
    """ORM model for t_map_task_files"""

    __tablename__ = "t_map_task_files"

    id: int | None = Field(default=None, sa_column=Column(BigInteger, primary_key=True, autoincrement=True))
    user_id: int = Field(sa_type=BigInteger)
    map_task_id: int = Field(sa_type=BigInteger)
    file_type: str = Field(max_length=15)
    file_path: str = Field(max_length=255)
    created_at: datetime | None = Field(default=None, sa_column=Column(DateTime, server_default=func.now()))
    updated_at: datetime | None = Field(default=None, sa_column=Column(DateTime, server_default=func.now(), onupdate=func.now()))


class MapTaskProgressDB(SQLModel, table=True):
    """ORM model for t_map_task_progress"""

    __tablename__ = "t_map_task_progress"

    id: int | None = Field(default=None, sa_column=Column(BigInteger, primary_key=True, autoincrement=True))
    map_task_id: int = Field(sa_type=BigInteger)
    percent: int = Field(default=0)  # 0-100
    description: str | None = Field(default=None, max_length=255)
    phase: str | None = Field(default=None, max_length=50)
    error_msg: str | None = Field(default=None, max_length=255)
    created_at: datetime | None = Field(default=None, sa_column=Column(DateTime, server_default=func.now()))
    updated_at: datetime | None = Field(default=None, sa_column=Column(DateTime, server_default=func.now(), onupdate=func.now()))


