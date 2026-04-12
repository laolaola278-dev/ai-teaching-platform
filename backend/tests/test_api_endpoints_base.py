import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def app():
    from app.main import app as _app  # type: ignore
    return _app


def test_health_endpoint(app):
    client = TestClient(app)
    resp = client.get('/health')
    assert resp.status_code == 200
    data = resp.json()
    assert data.get('status') == 'healthy'
    assert data.get('service') == 'ai-teaching-platform'


def test_root_endpoint(app):
    client = TestClient(app)
    resp = client.get('/')
    assert resp.status_code == 200
    data = resp.json()
    assert 'message' in data
    assert 'version' in data
    assert data.get('docs') == '/docs'
    assert data.get('redoc') == '/redoc'
