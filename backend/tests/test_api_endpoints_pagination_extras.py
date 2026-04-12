import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def app():
    from app.main import app as _app  # type: ignore
    return _app


def _monkeypatch_courses_pagination(monkeypatch):
    # Reuse the simplified FakeCourseService from test_api_endpoints.py if available
    class FakeCourseService:
        def __init__(self, db):
            pass
        async def get_courses(self, skip=0, limit=100):
            # return two items at most for pagination sanity
            return [
                {"id": "11111111-1111-1111-1111-111111111111", "title": "A", "description": "d", "source": "demo", "language": "en", "is_active": True},
                {"id": "22222222-2222-2222-2222-222222222222", "title": "B", "description": "d2", "source": "demo", "language": "en", "is_active": True},
            ][:limit]
        async def get_course(self, course_id):
            if course_id == "11111111-1111-1111-1111-111111111111":
                return {"id": course_id, "title": "A", "description": "d"}
            return None
    monkeypatch.setattr("app.api.v1.endpoints.courses.CourseService", FakeCourseService)
    monkeypatch.setattr("app.api.v1.endpoints.courses.get_db", lambda: None)


def test_list_courses_pagination(app, monkeypatch):
    _monkeypatch_courses_pagination(monkeypatch)
    client = TestClient(app)
    resp = client.get("/api/v1/courses/?skip=0&limit=2")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert len(data) <= 2
