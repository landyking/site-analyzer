from __future__ import annotations

from collections.abc import Iterable

from sqlalchemy import func
from sqlalchemy.sql import Select
from sqlmodel import Session, select

DEFAULT_PAGE_SIZE = 20
MAX_PAGE_SIZE = 200


def normalize_pagination(
    page_size: int | None,
    current_page: int | None,
    default_size: int = DEFAULT_PAGE_SIZE,
    max_size: int = MAX_PAGE_SIZE,
) -> tuple[int, int, int]:
    """Return (page_size, current_page, offset) with sane bounds.

    - page_size in [1, max_size]
    - current_page >= 1
    - offset = (current_page - 1) * page_size
    """
    ps = int(page_size or default_size)
    if ps < 1:
        ps = 1
    if ps > max_size:
        ps = max_size
    cp = int(current_page or 1)
    if cp < 1:
        cp = 1
    offset = (cp - 1) * ps
    return ps, cp, offset


def _scalar_count(session: Session, stmt) -> int:
    val = session.exec(stmt).one()
    try:
        if isinstance(val, tuple):
            val = val[0]
    except Exception:
        pass
    return int(val or 0)


def paginate(
    *,
    session: Session,
    base_stmt: Select,
    page_size: int | None,
    current_page: int | None,
    order_by: Iterable | None = None,
) -> tuple[list, int, int, int]:
    """Apply generic pagination to a SQLAlchemy/SQLModel Select.

    Returns (rows, total, page_size, current_page).
    """
    ps, cp, offset = normalize_pagination(page_size, current_page)

    # Count on a subquery to preserve filters without LIMIT/OFFSET/ORDER
    # Construct count as select(func.count()).select_from(subquery)
    count_stmt = select(func.count()).select_from(base_stmt.subquery())
    total = _scalar_count(session, count_stmt)

    stmt = base_stmt
    if order_by is not None:
        if isinstance(order_by, (list, tuple)):
            stmt = stmt.order_by(*order_by)
        else:
            stmt = stmt.order_by(order_by)
    stmt = stmt.offset(offset).limit(ps)
    rows = list(session.exec(stmt).all())
    return rows, int(total), ps, cp
