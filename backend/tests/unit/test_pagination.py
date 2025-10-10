import math

from sqlmodel import Field, Session, SQLModel, create_engine, select

from app.db.pagination import normalize_pagination, paginate


class Item(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str


def setup_items(n: int = 25) -> Session:
    engine = create_engine("sqlite://", echo=False)
    SQLModel.metadata.create_all(engine)
    with Session(engine) as s:
        for i in range(n):
            s.add(Item(name=f"item-{i}"))
        s.commit()
    return Session(engine)


class TestNormalizePagination:
    def test_defaults_and_bounds(self):
        ps, cp, off = normalize_pagination(page_size=None, current_page=None)
        assert (ps, cp, off) == (20, 1, 0)
        ps, cp, off = normalize_pagination(page_size=0, current_page=0)
        # page_size falls back to default when falsy -> 20
        assert (ps, cp, off) == (20, 1, 0)

        ps, cp, off = normalize_pagination(page_size=10_000, current_page=-5, max_size=200)
        assert (ps, cp, off) == (200, 1, 0)

        ps, cp, off = normalize_pagination(page_size=5, current_page=3)
        assert (ps, cp, off) == (5, 3, 10)


class TestPaginate:
    def test_simple_pagination(self):
        session = setup_items(25)
        try:
            base = select(Item)
            rows, total, ps, cp = paginate(
                session=session,
                base_stmt=base,
                page_size=10,
                current_page=2,
                order_by=Item.id.asc(),
            )
            assert total == 25
            assert ps == 10 and cp == 2
            assert isinstance(rows, list) and len(rows) == 10
            # page 2 starts from id 11 (1-indexed after autoincrement)
            assert rows[0].name == "item-10"
        finally:
            session.close()

    def test_order_by_multiple_and_last_page(self):
        session = setup_items(23)
        try:
            # order_by can be list/tuple
            rows, total, ps, cp = paginate(
                session=session,
                base_stmt=select(Item),
                page_size=7,
                current_page=math.ceil(23 / 7),
                # order by id to ensure numeric order rather than lexicographic name
                order_by=[Item.id.asc()],
            )
            assert total == 23 and ps == 7 and cp == 4
            # last page should have 2 items
            assert len(rows) == 2
            assert [r.name for r in rows] == ["item-21", "item-22"]
        finally:
            session.close()
