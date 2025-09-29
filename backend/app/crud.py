import json
import uuid
from typing import Any
from datetime import datetime, timezone
from app.core.config import settings
from fastapi import Depends, HTTPException, status

from sqlmodel import Session, select, delete
from fastapi import BackgroundTasks

from app.core.security import get_password_hash, verify_password
from app.models import (
    CreateMapTaskReq,
    MapTaskDB,
    MapTaskStatus,
    MapTaskProgressDB,
    MapTaskFileDB,
    UserDB,
    UserCreate,
    UserRole,
)
from pydantic.json import pydantic_encoder
from app.gis.processor import process_map_task
from app.db.pagination import paginate
from app.core import storage
import logging

logger = logging.getLogger(__name__)


def touch_last_login(*, session: Session, user: UserDB) -> UserDB:
    """Update the user's last_login to now (UTC) and persist.

    Returns the refreshed user row.
    """
    user.last_login = datetime.now(timezone.utc)
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


def create_user(*, session: Session, user_create: UserCreate) -> UserDB:
    if settings.RELEASE_ALLOW_REGISTRATION is False:
        raise HTTPException(
            status_code=400,
            detail="New user registration is disabled",
        )
    db_obj = UserDB.model_validate(
        user_create, update={"password_hash": get_password_hash(user_create.password)}
    )
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj


# def update_user(*, session: Session, db_user: User, user_in: UserUpdate) -> Any:
#     user_data = user_in.model_dump(exclude_unset=True)
#     extra_data = {}
#     if "password" in user_data:
#         password = user_data["password"]
#         hashed_password = get_password_hash(password)
#         extra_data["hashed_password"] = hashed_password
#     db_user.sqlmodel_update(user_data, update=extra_data)
#     session.add(db_user)
#     session.commit()
#     session.refresh(db_user)
#     return db_user


def get_user_by_email(*, session: Session, email: str) -> UserDB | None:
    statement = select(UserDB).where(UserDB.email == email)
    session_user = session.exec(statement).first()
    return session_user


def get_user_by_id(*, session: Session, user_id: int) -> UserDB | None:
    """Fetch a user by primary key id."""
    statement = select(UserDB).where(UserDB.id == user_id)
    return session.exec(statement).first()

def get_files_by_id(*, session: Session, user_id: int, map_task_id: int) -> list[MapTaskFileDB] | None:
    """Fetch files for a specific map task."""
    statement = select(MapTaskFileDB).where(
        MapTaskFileDB.user_id == user_id,
        MapTaskFileDB.map_task_id == map_task_id
    )
    return session.exec(statement).all()

def get_file_by_conditions(*, session: Session, map_task_id: int, file_type: str) -> MapTaskFileDB | None:
    """Fetch a specific file for a map task by tag."""
    statement = select(MapTaskFileDB).where(
        MapTaskFileDB.map_task_id == map_task_id,
        MapTaskFileDB.file_type == file_type
    )
    return session.exec(statement).first()

def authenticate(*, session: Session, email: str, password: str) -> UserDB | None:
    db_user = get_user_by_email(session=session, email=email)
    # print("Authenticating user...", db_user)
    if not db_user:
        return None
    if not verify_password(password, db_user.password_hash):
        return None
    # successful authentication – update last_login
    try:
        db_user = touch_last_login(session=session, user=db_user)
    except Exception:
        # Do not block login if timestamp update fails
        pass
    return db_user


# def create_item(*, session: Session, item_in: ItemCreate, owner_id: uuid.UUID) -> Item:
#     db_item = Item.model_validate(item_in, update={"owner_id": owner_id})
#     session.add(db_item)
#     session.commit()
#     session.refresh(db_item)
#     return db_item

def create_map_task(*, session: Session, user_id: int, payload: CreateMapTaskReq, background_tasks: BackgroundTasks | None = None) -> MapTaskDB:
    if settings.RELEASE_READ_ONLY:
        raise HTTPException(
            status_code=400,
            detail="System is in read-only mode; cannot create new tasks",
        )
    db_obj = MapTaskDB.model_validate(
        payload,
        update={
            "user_id": user_id,
            "status": MapTaskStatus.PENDING,
            "district": payload.district_code,
            "constraint_factors": json.dumps(payload.constraint_factors, default=pydantic_encoder),
            "suitability_factors": json.dumps(payload.suitability_factors , default=pydantic_encoder)
        }
    )
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    # Schedule background processing after successful insert
    if background_tasks is not None:
        background_tasks.add_task(process_map_task, db_obj.id)
    else:
        print("No background tasks available")
    return db_obj


def get_map_task(*, session: Session, user_id: int, task_id: int) -> MapTaskDB | None:
    """Fetch a map task by id for the given user."""
    statement = select(MapTaskDB).where(
        MapTaskDB.id == task_id,
        MapTaskDB.user_id == user_id,
    )
    return session.exec(statement).first()


def cancel_map_task(*, session: Session, user_id: int, task_id: int) -> MapTaskDB | None:
    """Cancel a user's map task if it exists. Returns the updated task or None if not found."""
    db_obj = get_map_task(session=session, user_id=user_id, task_id=task_id)
    if not db_obj:
        return None
    # Only update status if not already terminal; allow idempotent cancel
    if db_obj.status not in (MapTaskStatus.SUCCESS, MapTaskStatus.CANCELLED):
        db_obj.status = MapTaskStatus.CANCELLED
        # Ensure timezone-aware UTC datetime so API responses include timezone info
        db_obj.ended_at = db_obj.ended_at or datetime.now(timezone.utc)
        session.add(db_obj)
        session.commit()
        session.refresh(db_obj)
    return db_obj


def list_map_tasks(*, session: Session, user_id: int, completed: bool | None = None) -> list[MapTaskDB]:
    """List a user's map tasks with optional completion filter.

    completed=True  -> statuses in (SUCCESS, FAILURE, CANCELLED)
    completed=False -> statuses in (PENDING, PROCESSING)
    completed=None  -> no status filter
    """
    statement = select(MapTaskDB).where(MapTaskDB.user_id == user_id)
    if completed is True:
        statement = statement.where(
            MapTaskDB.status.in_([
                MapTaskStatus.SUCCESS,
                MapTaskStatus.FAILURE,
                MapTaskStatus.CANCELLED,
            ])
        )
    elif completed is False:
        statement = statement.where(
            MapTaskDB.status.in_([
                MapTaskStatus.PENDING,
                MapTaskStatus.PROCESSING,
            ])
        )
    # Order by newest first
    statement = statement.order_by(MapTaskDB.created_at.desc())
    return list(session.exec(statement).all())


def delete_map_task(*, session: Session, user_id: int, task_id: int) -> MapTaskDB | None:
    """Delete a user's map task if it exists and is not running.

    Returns the deleted task object (pre-delete) or None if not found.
    Raises ValueError if the task is still pending/processing and cannot be deleted safely.
    Also removes related files and progress rows when present.
    """
    db_obj = get_map_task(session=session, user_id=user_id, task_id=task_id)
    if not db_obj:
        return None
    if db_obj.status in (MapTaskStatus.PENDING, MapTaskStatus.PROCESSING):
        raise ValueError("Cannot delete a running task; cancel it first")

    # Fetch related file rows BEFORE deletion for storage cleanup
    file_rows: list[MapTaskFileDB] = []
    try:
        stmt_files = select(MapTaskFileDB).where(
            MapTaskFileDB.user_id == user_id,
            MapTaskFileDB.map_task_id == db_obj.id,
        )
        file_rows = list(session.exec(stmt_files).all())
    except Exception:
        logger.warning("Failed to fetch file rows for cleanup")
        file_rows = []

    # Attempt object storage deletion (best-effort, non-blocking)
    try:
        keys = [r.file_path for r in file_rows if r.file_path]
        if keys:
            storage.delete_files(keys)
    except Exception:
        logger.warning("Failed to delete files from storage")
        pass

    # Clean up related DB rows (best-effort; no cascading) then task
    try:
        session.exec(
            delete(MapTaskFileDB).where(
                MapTaskFileDB.user_id == user_id,
                MapTaskFileDB.map_task_id == db_obj.id,
            )
        )
        session.exec(
            delete(MapTaskProgressDB).where(
                MapTaskProgressDB.user_id == user_id,
                MapTaskProgressDB.map_task_id == db_obj.id,
            )
        )
    except Exception:
        logger.warning("Failed to delete related DB rows for task cleanup")
        pass

    session.delete(db_obj)
    session.commit()
    return db_obj


def duplicate_map_task(
    *,
    session: Session,
    user_id: int,
    task_id: int,
    background_tasks: BackgroundTasks | None = None,
) -> MapTaskDB | None:
    """Duplicate an existing map task for the same user and enqueue processing.

    Returns the newly created MapTaskDB or None if the source task is not found.
    """
    if settings.RELEASE_READ_ONLY:
        raise HTTPException(
            status_code=400,
            detail="System is in read-only mode; cannot create new tasks",
        )
    src = get_map_task(session=session, user_id=user_id, task_id=task_id)
    if not src:
        return None

    new_task = MapTaskDB(
        user_id=user_id,
        name=src.name,
        district=src.district,
        constraint_factors=src.constraint_factors,
        suitability_factors=src.suitability_factors,
        status=MapTaskStatus.PENDING,
        error_msg=None,
        started_at=None,
        ended_at=None,
    )
    session.add(new_task)
    session.commit()
    session.refresh(new_task)

    if background_tasks is not None:
        background_tasks.add_task(process_map_task, new_task.id)
    return new_task

def get_map_task_progress(*, session: Session, user_id: int, task_id: int) -> list[MapTaskProgressDB]:
    """Get the progress rows for a specific map task."""
    statement = select(MapTaskProgressDB).where(MapTaskProgressDB.user_id == user_id, 
                                                MapTaskProgressDB.map_task_id == task_id).order_by(MapTaskProgressDB.created_at.asc())
    rows = session.exec(statement).all()
    return rows

def admin_get_map_task_progress(*, session: Session, task_id: int) -> list[MapTaskProgressDB]:
    """Get the progress rows for a specific map task."""
    statement = select(MapTaskProgressDB).where(MapTaskProgressDB.map_task_id == task_id).order_by(MapTaskProgressDB.created_at.asc())
    rows = session.exec(statement).all()
    return rows


def admin_get_map_task(*, session: Session, task_id: int) -> MapTaskDB | None:
    """Fetch a map task by id without user restriction (admin scope)."""
    statement = select(MapTaskDB).where(MapTaskDB.id == task_id)
    return session.exec(statement).first()


def admin_list_users(
    *,
    session: Session,
    page_size: int,
    current_page: int,
    keyword: str | None = None,
    status: int | None = None,
) -> tuple[list[UserDB], int, int, int]:
    """List users for admin with pagination and optional filters.

    Returns (rows, total_count, page_size, current_page).
    """
    # Base selectable
    stmt = select(UserDB)

    # Filters
    if keyword:
        kw = f"%{keyword.strip()}%"
        stmt = stmt.where(UserDB.email.like(kw))
    if status is not None:
        stmt = stmt.where(UserDB.status == status)

    # Paginate with consistent ordering
    rows, total, ps, cp = paginate(
        session=session,
        base_stmt=stmt,
        page_size=page_size,
        current_page=current_page,
        order_by=(UserDB.created_at.desc(),),
    )
    return rows, total, ps, cp


def admin_list_map_tasks(
    *,
    session: Session,
    page_size: int,
    current_page: int,
    name: str | None = None,
    user_id: int | None = None,
    status: int | None = None,
) -> tuple[list[MapTaskDB], int, int, int]:
    """List map tasks for admin with pagination and optional filters."""
    stmt = select(MapTaskDB)
    if name:
        kw = f"%{name.strip()}%"
        stmt = stmt.where(MapTaskDB.name.like(kw))
    if user_id is not None:
        stmt = stmt.where(MapTaskDB.user_id == user_id)
    if status is not None:
        stmt = stmt.where(MapTaskDB.status == status)

    rows, total, ps, cp = paginate(
        session=session,
        base_stmt=stmt,
        page_size=page_size,
        current_page=current_page,
        order_by=(MapTaskDB.created_at.desc(),),
    )
    return rows, total, ps, cp


def admin_update_user_status(
    *, session: Session, target_user_id: int, status: int
) -> UserDB | None:
    """Update a user's status (admin only action).

    Validates status against UserStatus enum. Returns updated user or None if not found.
    Raises ValueError for invalid status input.
    """
    # Fetch target user
    stmt = select(UserDB).where(UserDB.id == target_user_id)
    user = session.exec(stmt).first()
    if not user:
        return None
    if user.role == UserRole.ADMIN:
        return None  # Do not allow changing admin status
    # Update and persist only if changed
    new_status = int(status)
    if user.status != new_status:
        user.status = new_status
        session.add(user)
        session.commit()
        session.refresh(user)
    return user