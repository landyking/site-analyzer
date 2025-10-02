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


def test_user_login_incorrect_password():
    app = _make_app_for_auth()
    client = TestClient(app)
    with patch("app.api.routes.auth.crud.authenticate", return_value=None):
        r = client.post("/user-login", data={"username": "u@e.com", "password": "bad"})
        assert r.status_code == 400


def test_user_login_inactive_user():
    app = _make_app_for_auth()
    client = TestClient(app)
    inactive_user = MagicMock(id=1, role=UserRole.USER, status=UserStatus.LOCKED)
    with patch("app.api.routes.auth.crud.authenticate", return_value=inactive_user):
        r = client.post("/user-login", data={"username": "u@e.com", "password": "x"})
        assert r.status_code == 400


def test_oidc_info_endpoint():
    app = _make_app_for_auth()
    client = TestClient(app)
    r = client.get("/oidc-info")
    assert r.status_code == 200
    assert "login_url" in r.json()


def test_oidc_token_missing_id_token():
    app = _make_app_for_auth()
    client = TestClient(app)
    class Resp:
        status_code = 200
        def json(self):
            return {"access_token": "abc", "token_type": "bearer"}
    with patch("app.api.routes.auth.requests.post", return_value=Resp()):
        r = client.post("/oidc-token", json={"code": "dummy"})
        assert r.status_code == 400


def test_oidc_token_exchange_error():
    app = _make_app_for_auth()
    client = TestClient(app)
    class Resp:
        status_code = 500
        text = "error"
        def json(self):
            return {}
    with patch("app.api.routes.auth.requests.post", return_value=Resp()):
        r = client.post("/oidc-token", json={"code": "dummy"})
        assert r.status_code == 400


def test_oidc_token_invalid_jwt_decode():
    app = _make_app_for_auth()
    client = TestClient(app)
    class Resp:
        status_code = 200
        def json(self):
            return {"id_token": "xyz"}
    with patch("app.api.routes.auth.requests.post", return_value=Resp()), \
         patch("app.api.routes.auth.jwt.decode", side_effect=Exception("bad token")):
        r = client.post("/oidc-token", json={"code": "dummy"})
        assert r.status_code == 400


def test_oidc_token_success_flow():
    app = _make_app_for_auth()
    client = TestClient(app)
    class Resp:
        status_code = 200
        def json(self):
            return {"id_token": "xyz", "refresh_token": "r"}
    decoded = {"email": "g@example.com", "sub": "sub123", "email_verified": True}
    user_obj = MagicMock(id=2, role=UserRole.USER, status=UserStatus.ACTIVE)
    with patch("app.api.routes.auth.requests.post", return_value=Resp()), \
         patch("app.api.routes.auth.jwt.decode", return_value=decoded), \
         patch("app.api.routes.auth.crud.get_user_by_email", return_value=None), \
         patch("app.api.routes.auth.crud.create_user", return_value=user_obj), \
         patch("app.api.routes.auth.crud.touch_last_login", return_value=user_obj), \
         patch("app.api.routes.auth.security.create_access_token", return_value="tok"):
        r = client.post("/oidc-token", json={"code": "dummy"})
        assert r.status_code == 200
        body = r.json()
        assert body["access_token"] == "tok"
