from types import SimpleNamespace
from unittest.mock import patch

from app.core.db_init import init_db


class FakeResult:
    def __init__(self, value):
        self._value = value

    def first(self):
        return self._value


class FakeSession:
    def __init__(self, result_value):
        self._result_value = result_value

    def exec(self, *args, **kwargs):
        return FakeResult(self._result_value)


def test_init_db_creates_superuser_when_missing():
    session = FakeSession(result_value=None)
    with patch(
        "app.core.db_init.crud.create_user", return_value=SimpleNamespace(id=1)
    ) as create_user:
        init_db(session)
        create_user.assert_called_once()


def test_init_db_noop_when_superuser_exists():
    # Simulate a user being returned from DB
    existing_user = SimpleNamespace(id=1, email="admin@example.com")
    session = FakeSession(result_value=existing_user)
    with patch("app.core.db_init.crud.create_user") as create_user:
        init_db(session)
        create_user.assert_not_called()
