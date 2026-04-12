import json
from fastapi.testclient import TestClient
import importlib
import types
import pytest


@pytest.fixture
def app():
    # Import the FastAPI app from the existing codebase
    from app.main import app as _app  # type: ignore
    return _app


class FakeCourseService:
    def __init__(self, db):
        pass

    async def get_courses(self, skip=0, limit=100):
        return [
            {
                "id": "11111111-1111-1111-1111-111111111111",
                "title": "Test Course",
                "description": "desc",
                "source": "demo",
                "language": "en",
                "is_active": True,
                "created_at": "2020-01-01T00:00:00Z",
                "updated_at": "2020-01-01T00:00:00Z",
            }
        ]

    async def get_course(self, course_id):
        if course_id == "11111111-1111-1111-1111-111111111111":
            return {
                "id": course_id,
                "title": "Test Course",
                "description": "desc",
                "source": "demo",
                "language": "en",
                "is_active": True,
                "created_at": "2020-01-01T00:00:00Z",
                "updated_at": "2020-01-01T00:00:00Z",
            }
        return None

    async def create_course(self, course_create):
        return {
            "id": "22222222-2222-2222-2222-222222222222",
            "title": course_create.title,
            "source": course_create.source,
            "language": course_create.language,
            "description": course_create.description,
            "is_active": True,
            "created_at": "2020-01-01T00:00:00Z",
            "updated_at": "2020-01-01T00:00:00Z",
        }

    async def update_course(self, course_id, update_data):
        return {"id": course_id, **update_data}

    async def delete_course(self, course_id):
        return True


def _monkeypatch_services(monkeypatch):
    # Patch the CourseService used by the courses endpoints to a fake one
    monkeypatch.setattr("app.api.v1.endpoints.courses.CourseService", FakeCourseService)
    # Ensure the DB dependency does not try to establish a real DB connection
    monkeypatch.setattr("app.api.v1.endpoints.courses.get_db", lambda: None)


def test_list_courses_endpoint(app, monkeypatch):
    _monkeypatch_services(monkeypatch)
    client = TestClient(app)
    resp = client.get("/api/v1/courses/")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert len(data) >= 0


def test_get_course_found(app, monkeypatch):
    _monkeypatch_services(monkeypatch)
    client = TestClient(app)
    resp = client.get("/api/v1/courses/11111111-1111-1111-1111-111111111111")
    assert resp.status_code == 200
    payload = resp.json()
    assert payload.get("id") == "11111111-1111-1111-1111-111111111111"


def test_get_course_not_found(app, monkeypatch):
    _monkeypatch_services(monkeypatch)
    client = TestClient(app)
    resp = client.get("/api/v1/courses/00000000-0000-0000-0000-000000000000")
    assert resp.status_code == 404


def test_create_course(app, monkeypatch):
    _monkeypatch_services(monkeypatch)
    client = TestClient(app)
    payload = {
        "title": "New Course",
        "source": "demo",
        "language": "en",
        "description": "desc",
        "is_active": True,
    }
    resp = client.post("/api/v1/courses/", json=payload)
    assert resp.status_code == 201
    data = resp.json()
    assert data.get("title") == payload["title"]


def test_update_course(app, monkeypatch):
    _monkeypatch_services(monkeypatch)
    client = TestClient(app)
    payload = {"title": "Updated Title"}
    resp = client.put("/api/v1/courses/11111111-1111-1111-1111-111111111111", json=payload)
    assert resp.status_code in (200, 201)


def test_delete_course(app, monkeypatch):
    _monkeypatch_services(monkeypatch)
    client = TestClient(app)
    resp = client.delete("/api/v1/courses/11111111-1111-1111-1111-111111111111")
    assert resp.status_code == 204
