from fastapi import FastAPI
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

from app.api.main import api_router
from app.api import deps as deps_module
from app.models import UserRole, UserStatus


class DummyUser:
    def __init__(self, uid: int = 1, admin: bool = False):
        self.id = uid
        self.role = UserRole.ADMIN if admin else UserRole.USER
        self.status = UserStatus.ACTIVE
        self.email = "user@example.com"
        self.provider = "local"
        self.sub = "sub"


def _make_app_for_auth():
    app = FastAPI()
    app.include_router(api_router)

    def override_get_db():
        yield MagicMock()

    def override_current_user():
        return DummyUser(1, admin=False)

    app.dependency_overrides[deps_module.get_db] = override_get_db
    app.dependency_overrides[deps_module.get_current_user] = override_current_user
    return app


def test_user_info_endpoint_returns_current_user():
    app = _make_app_for_auth()
    client = TestClient(app)
    resp = client.post("/user-info")
    assert resp.status_code == 200
    data = resp.json()
    assert data["email"] == "user@example.com"


def test_user_register_duplicate_and_success():
    app = _make_app_for_auth()
    client = TestClient(app)
    # duplicate
    with patch("app.api.routes.auth.crud.get_user_by_email", return_value=MagicMock(id=1)):
        r = client.post("/user-register", json={"email": "u@e.com", "password": "12345678"})
        assert r.status_code == 400
    # success
    with patch("app.api.routes.auth.crud.get_user_by_email", return_value=None), \
         patch("app.api.routes.auth.crud.create_user", return_value=MagicMock(id=2, email="u@e.com", provider="local", sub="u@e.com", role=UserRole.USER, status=UserStatus.LOCKED)):
        r = client.post("/user-register", json={"email": "u@e.com", "password": "12345678"})
        assert r.status_code == 200
        body = r.json()
        assert body["email"] == "u@e.com"
