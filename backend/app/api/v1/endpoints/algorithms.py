"""API endpoints for algorithm training and inference (skeleton)."""
from __future__ import annotations

from typing import Dict
import uuid

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.api.v1.dependencies import get_db
from app.api.v1.dependencies.auth import get_current_user, require_role
from app.api.v1.dependencies.auth import get_current_user
from app.services.algorithm_service import AlgorithmService
from app.schemas.algorithm import TrainingJob as TrainingJobSchema
from app.schemas.algorithm import TrainingJobCreate, TrainingJobUpdate, AlgorithmRequest
from app.schemas.algorithm import TrainingStatus
import asyncio
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession


router = APIRouter()


class TrainRequest(BaseModel):
    algorithm_type: str
    parameters: Dict[str, object] = {}
    config: Dict[str, object] = {}


class PredictRequest(BaseModel):
    algorithm_type: str
    input_data: list[object] = []
    model_id: str | None = None
    parameters: Dict[str, object] = {}


@router.post("/train", response_model=TrainingJobSchema)
async def train_algorithm(req: AlgorithmRequest, db: AsyncSession = Depends(get_db), current_user: dict = Depends(get_current_user), _admin: bool = Depends(require_role("admin"))):
    """Create a new training job and kick off training (async)."""
    service = AlgorithmService(db)
    job = await service.create_training_job(req)
    # schedule background execution
    asyncio.create_task(service.execute_training(job.id, req))
    return job


@router.post("/predict", response_model=dict)
async def predict_algorithm(req: PredictRequest, db=Depends(get_db)):
    """Skeleton endpoint to run a prediction."""
    # Placeholder response; a real implementation would load a model and run inference.
    return {
        "algorithm_type": req.algorithm_type,
        "model_id": req.model_id,
        "predictions": [],
        "notes": "This is a skeleton endpoint; integrate with actual model runner.",
    }

@router.get("/jobs", response_model=list[TrainingJobSchema])
async def list_training_jobs(skip: int = 0, limit: int = 50, status: Optional[str] = None, db: AsyncSession = Depends(get_db)):
    service = AlgorithmService(db)
    s = TrainingStatus(status) if status is not None else None
    jobs = await service.get_training_jobs(skip=skip, limit=limit, status=s)
    return jobs

@router.get("/jobs/{job_id}", response_model=TrainingJobSchema)
async def get_training_job(job_id: str, db: AsyncSession = Depends(get_db)):
    service = AlgorithmService(db)
    job = await service.get_training_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Training job not found")
    return job

@router.patch("/jobs/{job_id}", response_model=TrainingJobSchema)
async def update_training_job(job_id: str, update: TrainingJobUpdate, db: AsyncSession = Depends(get_db)):
    service = AlgorithmService(db)
    updated = await service.update_training_job(UUID(job_id) if isinstance(job_id, str) else job_id, update.model_dump(exclude_unset=True))
    if not updated:
        raise HTTPException(status_code=404, detail="Training job not found")
    return updated

@router.delete("/jobs/{job_id}")
async def delete_training_job(job_id: str, db: AsyncSession = Depends(get_db)):
    service = AlgorithmService(db)
    success = await service.repository.delete_training_job(UUID(job_id)) if hasattr(service, 'repository') else False
    if not success:
        raise HTTPException(status_code=404, detail="Training job not found")
    return {"status": "deleted"}
