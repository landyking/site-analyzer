from __future__ import annotations

from datetime import datetime
from typing import List, Optional, Annotated

from pydantic import BaseModel, EmailStr
from sqlmodel import Field, Relationship, SQLModel
from sqlalchemy import Column, DateTime, Index, BigInteger
from sqlalchemy.sql import func
from enum import Enum, IntEnum


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


class MapTaskDB(SQLModel, table=True):
    """ORM model for t_map_task"""

    __tablename__ = "t_map_task"

    id: Optional[int] = Field(
        default=None,
        sa_column=Column(BigInteger, primary_key=True, autoincrement=True),
    )
    user_id: int = Field(foreign_key="t_user.id", sa_type=BigInteger)
    name: str = Field(max_length=150)
    district: str = Field(max_length=10)
    # status: 1 Pending, 2 Processing, 3 Success, 4 Failure, 5 Cancelled
    status: int = Field(default=1)
    error_msg: Optional[str] = Field(default=None, max_length=255)
    # Stored as JSON string in TEXT column
    constraint_factors: str = Field(default="[]")
    suitability_factors: str = Field(default="[]")
    started_at: Optional[datetime] = Field(default=None, sa_column=Column(DateTime))
    ended_at: Optional[datetime] = Field(default=None, sa_column=Column(DateTime))
    created_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime, server_default=func.now()),
    )
    updated_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime, server_default=func.now(), onupdate=func.now()),
    )

    # relationships
    # user: Optional["UserDB"] = Relationship(back_populates="tasks")
    # files: List["MapTaskFileDB"] = Relationship(back_populates="map_task")


class MapTaskFileDB(SQLModel, table=True):
    """ORM model for t_map_task_files"""

    __tablename__ = "t_map_task_files"

    id: Optional[int] = Field(
        default=None,
        sa_column=Column(BigInteger, primary_key=True, autoincrement=True),
    )
    user_id: int = Field(foreign_key="t_user.id", sa_type=BigInteger)
    map_task_id: int = Field(foreign_key="t_map_task.id", sa_type=BigInteger)
    file_type: str = Field(max_length=15)
    file_path: str = Field(max_length=255)
    created_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime, server_default=func.now()),
    )
    updated_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime, server_default=func.now(), onupdate=func.now()),
    )

    # relationships
    # user: Optional["UserDB"] = Relationship(back_populates="files")
    # map_task: Optional["MapTaskDB"] = Relationship(back_populates="files")

