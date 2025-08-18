import json
import uuid
from typing import Any
from datetime import datetime

from sqlmodel import Session, select
from fastapi import BackgroundTasks

from app.core.security import get_password_hash, verify_password
from app.models import CreateMapTaskReq, MapTaskDB, MapTaskStatus, UserDB, UserCreate
from pydantic.json import pydantic_encoder
from app.gis.processor import process_map_task



def create_user(*, session: Session, user_create: UserCreate) -> UserDB:
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


def authenticate(*, session: Session, email: str, password: str) -> UserDB | None:
    db_user = get_user_by_email(session=session, email=email)
    # print("Authenticating user...", db_user)
    if not db_user:
        return None
    if not verify_password(password, db_user.password_hash):
        return None
    return db_user


# def create_item(*, session: Session, item_in: ItemCreate, owner_id: uuid.UUID) -> Item:
#     db_item = Item.model_validate(item_in, update={"owner_id": owner_id})
#     session.add(db_item)
#     session.commit()
#     session.refresh(db_item)
#     return db_item

def create_map_task(*, session: Session, user_id: int, payload: CreateMapTaskReq, background_tasks: BackgroundTasks | None = None) -> MapTaskDB:
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
        db_obj.ended_at = db_obj.ended_at or datetime.utcnow()
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