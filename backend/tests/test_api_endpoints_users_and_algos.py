import json
import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def app():
    from app.main import app as _app  # type: ignore
    return _app


def _monkeypatch_user_endpoints(monkeypatch):
    class FakeUserService:
        def __init__(self, db):
            pass
        async def get_users(self, skip=0, limit=100):
            return []
        async def get_user(self, user_id):
            if str(user_id) == '123':
                return {"id": "123", "username": "alice", "email": "alice@example.com", "full_name": "Alice"}
            return None
        async def create_user(self, user_create):
            return {"id": "new-user-id", "username": user_create.username, "email": user_create.email, "full_name": user_create.full_name}
        async def update_user(self, user_id, user_update):
            return {"id": user_id, **(user_update.model_dump(exclude_unset=True))}
        async def delete_user(self, user_id):
            return True

    monkeypatch.setattr("app.api.v1.endpoints.users.UserService", FakeUserService)
    monkeypatch.setattr("app.api.v1.endpoints.users.get_db", lambda: None)

def test_users_crud_endpoints(app, monkeypatch):
    _monkeypatch_user_endpoints(monkeypatch)
    client = TestClient(app)

    resp = client.get('/api/v1/users/')
    assert resp.status_code == 200

    resp = client.get('/api/v1/users/123')
    assert resp.status_code == 200
    assert resp.json().get('id') == '123'

    # Create
    payload = {"username": "newuser", "email": "new@example.com", "password": "passwd123", "full_name": "New User"}
    resp = client.post('/api/v1/users/', json=payload)
    assert resp.status_code == 201
    data = resp.json()
    assert data.get('username') == 'newuser'

    # Update
    update_payload = {"full_name": "Updated"}
    resp = client.put('/api/v1/users/123', json=update_payload)
    assert resp.status_code == 200

    # Delete
    resp = client.delete('/api/v1/users/123')
    assert resp.status_code == 204
