from __future__ import annotations

import json
from datetime import UTC, datetime
from typing import Any

from app import crud
from app.core import storage
from app.gis.consts import districts
from app.models import (
    MapTask,
    MapTaskDB,
    MapTaskDetails,
    MapTaskFile,
    MapTaskFileDB,
    MapTaskStatus,
)

# Build a fast lookup for district code -> name
_DISTRICT_CODE_TO_NAME = {code: name for code, name in districts}


def _ensure_list(val):
    return json.loads(val) if isinstance(val, str) else val


def as_aware_utc(dt: datetime | None) -> datetime | None:
    if dt is None:
        return None
    if dt.tzinfo is None:
        return dt.replace(tzinfo=UTC)
    return dt.astimezone(UTC)


def _status_desc(status: int) -> str | None:
    try:
        return MapTaskStatus(status).name.title()
    except Exception:
        return None


def to_map_task(session: Any, data: MapTaskDB) -> MapTask:
    """Map a MapTaskDB row to API MapTask (without files)."""
    # Get user email (best effort)
    user_email: str | None = None
    try:
        user = crud.get_user_by_id(session=session, user_id=data.user_id)
        if user:
            user_email = user.email
    except Exception:
        user_email = None

    district_name = _DISTRICT_CODE_TO_NAME.get(data.district)
    return MapTask(
        id=data.id,
        name=data.name,
        user_id=data.user_id,
        user_email=user_email,
        district_code=data.district,
        district_name=district_name,
        status=data.status,
        status_desc=_status_desc(data.status),
        started_at=as_aware_utc(data.started_at),
        ended_at=as_aware_utc(data.ended_at),
        created_at=as_aware_utc(data.created_at),
    )


def to_map_task_details(session: Any, data: MapTaskDB) -> MapTaskDetails:
    """Map MapTaskDB to MapTaskDetails, including files and parsed factors."""
    base = to_map_task(session, data)

    # Files with presigned URLs
    db_files: list[MapTaskFileDB] = crud.get_files_by_id(
        session=session, user_id=data.user_id, map_task_id=data.id
    )
    files: list[MapTaskFile] = [MapTaskFile(**file.model_dump()) for file in db_files]
    for f in files:
        f.file_path = storage.generate_presigned_url(f.file_path)

    return MapTaskDetails(
        id=base.id,
        name=base.name,
        user_id=base.user_id,
        user_email=base.user_email,
        district_code=base.district_code,
        district_name=base.district_name,
        status=base.status,
        status_desc=base.status_desc,
        started_at=base.started_at,
        ended_at=base.ended_at,
        created_at=base.created_at,
        files=files,
        constraint_factors=_ensure_list(data.constraint_factors),
        suitability_factors=_ensure_list(data.suitability_factors),
    )
