from fastapi import FastAPI
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch
from types import SimpleNamespace
from datetime import datetime

from app.api.main import api_router


def make_app_with_overrides(current_user_is_admin: bool = False):
    app = FastAPI()
    app.include_router(api_router)

    # Dependency overrides for auth and DB
    from app.api import deps as deps_module
    from app.models import UserRole, UserStatus

    class DummyUser:
        def __init__(self, uid: int = 1, admin: bool = False):
            self.id = uid
            self.role = UserRole.ADMIN if admin else UserRole.USER
            self.status = UserStatus.ACTIVE

    def override_get_db():
        # Match Depends(get_db) which yields a Session
        yield MagicMock()

    def override_get_current_user():
        return DummyUser(1, admin=False)

    def override_get_current_admin():
        return DummyUser(1, admin=True if current_user_is_admin else False)

    app.dependency_overrides[deps_module.get_db] = override_get_db
    app.dependency_overrides[deps_module.get_current_user] = override_get_current_user
    app.dependency_overrides[deps_module.get_current_active_admin] = override_get_current_admin

    return app


def test_auth_user_login_calls_crud_authenticate():
    app = make_app_with_overrides()
    client = TestClient(app)
    with patch("app.crud.authenticate", return_value=MagicMock(id=1, status=1, role=0)) as auth_mock, \
         patch("app.core.security.create_access_token", return_value="token"):
        resp = client.post("/user-login", data={"username": "a@b.com", "password": "x"})
        assert resp.status_code == 200
        auth_mock.assert_called_once()


def test_user_select_options_endpoints():
    app = make_app_with_overrides()
    client = TestClient(app)
    # districts
    r = client.get("/user/select-options/district?limit=2&keyword=a")
    assert r.status_code == 200
    body = r.json()
    assert body["error"] == 0
    assert isinstance(body["list"], list)

    # constraint factors
    r = client.get("/user/select-options/constraint-factors?limit=2")
    assert r.status_code == 200
    body = r.json()
    assert body["error"] == 0

    # my map tasks listing (mock crud)
    with patch("app.api.routes.user.crud.list_map_tasks", return_value=[]):
        r = client.get("/user/my-map-tasks")
        assert r.status_code == 200
        assert r.json()["error"] == 0


def test_admin_inputs_initialize_uses_storage():
    app = make_app_with_overrides(current_user_is_admin=True)
    client = TestClient(app)
    with patch("app.core.storage.initialize_input_dir_from_bucket", return_value={"downloaded": 0, "archives": 0, "extracted_files": 0}) as init_mock:
        r = client.get("/admin/inputs-initialize")
        assert r.status_code == 200
        init_mock.assert_called_once()

def test_admin_users_list_endpoint():
    app = make_app_with_overrides(current_user_is_admin=True)
    client = TestClient(app)
    # mock admin_list_users to avoid touching DB
    fake_row = MagicMock(
        id=1,
        provider="local",
        sub="sub",
        email="a@b.com",
        role=0,
        status=1,
        created_at="2024-01-01T00:00:00Z",
        last_login="2024-01-02T00:00:00Z",
    )
    with patch("app.api.routes.admin.crud.admin_list_users", return_value=([fake_row], 1, 20, 1)):
        r = client.get("/admin/users?page_size=20&current_page=1")
        assert r.status_code == 200
        body = r.json()
        assert body["error"] == 0
        assert body["total"] == 1
        assert isinstance(body["list"], list)

def test_user_get_map_task_not_found():
    app = make_app_with_overrides()
    client = TestClient(app)
    with patch("app.api.routes.user.crud.get_map_task", return_value=None):
        r = client.get("/user/my-map-tasks/12345")
        assert r.status_code == 404

def test_admin_map_tasks_list_endpoint():
    app = make_app_with_overrides(current_user_is_admin=True)
    client = TestClient(app)
    fake_row = SimpleNamespace(
        id=1,
        name="task",
        user_id=1,
        district="A",
        status=1,
        started_at=None,
        ended_at=None,
        created_at=datetime.utcnow(),
    )
    with patch("app.api.routes.admin.crud.admin_list_map_tasks", return_value=([fake_row], 1, 20, 1)), \
         patch("app.api.routes._mappers.crud.get_user_by_id", return_value=MagicMock(email="a@b.com")):
        r = client.get("/admin/map-tasks?page_size=20&current_page=1")
        assert r.status_code == 200
        body = r.json()
        assert body["error"] == 0
        assert body["total"] == 1
        
    def test_admin_map_task_progress_lists_rows():
        app = make_app_with_overrides(current_user_is_admin=True)
        client = TestClient(app)
        row = SimpleNamespace(
            id=1,
            map_task_id=2,
            percent=20,
            description=None,
            phase=None,
            error_msg=None,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            model_dump=lambda: {
                "id": 1,
                "map_task_id": 2,
                "percent": 20,
                "description": None,
                "phase": None,
                "error_msg": None,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
            },
        )
        with patch("app.api.routes.admin.crud.admin_get_map_task_progress", return_value=[row]):
            r = client.get("/admin/map-tasks/2/progress")
            assert r.status_code == 200
            body = r.json()
            assert body["error"] == 0
            assert isinstance(body["list"], list)

def test_user_district_histograms_success():
    app = make_app_with_overrides()
    client = TestClient(app)
    # Choose a known district code from HISTOGRAMS file; '063' exists
    r = client.get("/user/districts/063/histograms")
    assert r.status_code == 200
    body = r.json()
    assert body["error"] == 0
    assert isinstance(body["list"], list)

def test_user_map_task_progress_lists_rows():
    app = make_app_with_overrides()
    client = TestClient(app)
    row = SimpleNamespace(
        id=1,
        map_task_id=2,
        percent=10,
        description=None,
        phase=None,
        error_msg=None,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
        model_dump=lambda: {
            "id": 1,
            "map_task_id": 2,
            "percent": 10,
            "description": None,
            "phase": None,
            "error_msg": None,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        },
    )
    with patch("app.api.routes.user.crud.get_map_task_progress", return_value=[row]):
        r = client.get("/user/my-map-tasks/2/progress")
        assert r.status_code == 200
        body = r.json()
        assert body["error"] == 0
        assert isinstance(body["list"], list)

def test_auth_logout_and_refresh():
    app = make_app_with_overrides()
    client = TestClient(app)
    # token refresh
    r = client.post("/user/token-refresh")
    assert r.status_code == 200
    body = r.json()
    assert body["error"] == 0
    assert body["access_token"] == "refreshed"
    # logout
    r = client.post("/user/logout")
    assert r.status_code == 200
    assert r.json()["error"] == 0
