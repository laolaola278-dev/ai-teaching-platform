import asyncio
import uuid
import pytest

from app.schemas.algorithm import AlgorithmRequest


class FakeAlgorithmRepository:
    def __init__(self, db):
        self.db = db
        self.jobs = {}

    async def create_training_job(self, job_data: dict):
        jid = str(uuid.uuid4())
        job = dict(job_data)
        job["id"] = jid
        self.jobs[jid] = job
        return job

    async def get_training_job(self, job_id):
        return self.jobs.get(str(job_id))

    async def get_training_jobs(self, skip=0, limit=100, status=None):
        items = list(self.jobs.values())
        if status is not None:
            items = [j for j in items if j.get("status") == status]
        return items[skip:skip+limit]

    async def update_training_job(self, job_id, update_data):
        j = self.jobs.get(str(job_id))
        if not j:
            return None
        j.update(update_data)
        self.jobs[str(job_id)] = j
        return j

    async def delete_training_job(self, job_id):
        if str(job_id) in self.jobs:
            del self.jobs[str(job_id)]
            return True
        return False


@pytest.mark.asyncio
async def test_create_training_job_and_get(monkeypatch):
    import app.repositories.algorithm_repository as ar
    monkeypatch.setattr(ar, "AlgorithmRepository", lambda db: FakeAlgorithmRepository(db))
    from app.services.algorithm_service import AlgorithmService
    service = AlgorithmService(db=None)
    req = AlgorithmRequest(algorithm_type="linear_regression", parameters={"X": [[1]], "y": [1]}, config={})
    job = await service.create_training_job(req)
    assert job.get("algorithm_type") == "linear_regression"
    assert "id" in job
