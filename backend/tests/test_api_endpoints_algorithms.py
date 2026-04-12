import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def app():
    from app.main import app as _app  # type: ignore
    return _app


import uuid

class FakeAlgorithmService:
    def __init__(self, db):
        pass
    async def create_training_job(self, request):
        return {
            "id": str(uuid.uuid4()),
            "algorithm_type": request.algorithm_type,
            "status": "pending",
            "progress": 0,
            "started_at": None,
            "completed_at": None,
            "user_id": None,
            "created_at": "2020-01-01T00:00:00Z",
            "updated_at": "2020-01-01T00:00:00Z",
            "result": None,
        }
    async def get_training_job(self, job_id):
        return {"id": job_id, "status": "completed", "progress": 100}
    async def get_training_jobs(self, skip=0, limit=100, status=None):
        return []
    async def update_training_job(self, job_id, update_data):
        return {"id": job_id, **update_data}


def _monkeypatch_algos(monkeypatch):
    monkeypatch.setattr("app.api.v1.endpoints.algorithms.AlgorithmService", FakeAlgorithmService)
    monkeypatch.setattr("app.api.v1.endpoints.algorithms.get_db", lambda: None)


def test_algorithm_train_and_get(app, monkeypatch):
    _monkeypatch_algos(monkeypatch)
    client = TestClient(app)
    payload = {"algorithm_type": "linear_regression", "parameters": {"X": [[1],[2]], "y": [1,2]}, "config": {}}
    resp = client.post("/api/v1/algorithms/train", json=payload)
    assert resp.status_code == 200 or resp.status_code == 201
    data = resp.json()
    assert "id" in data
    job_id = data["id"]
    resp = client.get(f"/api/v1/algorithms/jobs/{job_id}")
    assert resp.status_code == 200
