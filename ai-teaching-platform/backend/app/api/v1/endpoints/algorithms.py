"""
Algorithm engine API endpoints for interactive teaching.
"""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any, List

from app.core.database import get_db
from app.schemas.algorithm import (
    AlgorithmRequest,
    AlgorithmResponse,
    TrainingJob,
    TrainingStatus,
)
from app.services.algorithm_service import AlgorithmService

router = APIRouter()


@router.post("/train", response_model=TrainingJob)
async def train_algorithm(
    request: AlgorithmRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
) -> TrainingJob:
    """Start a training job for an algorithm."""
    service = AlgorithmService(db)
    
    # Validate algorithm type
    if request.algorithm_type not in ["linear_regression", "cnn", "transformer"]:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported algorithm type: {request.algorithm_type}"
        )
    
    # Create training job
    job = await service.create_training_job(request)
    
    # Start training in background
    background_tasks.add_task(
        service.execute_training,
        job_id=job.id,
        request=request,
    )
    
    return job


@router.get("/jobs/{job_id}", response_model=TrainingJob)
async def get_training_job(
    job_id: str,
    db: AsyncSession = Depends(get_db),
) -> TrainingJob:
    """Get the status of a training job."""
    service = AlgorithmService(db)
    job = await service.get_training_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Training job not found")
    return job


@router.get("/jobs", response_model=List[TrainingJob])
async def list_training_jobs(
    skip: int = 0,
    limit: int = 100,
    status: str | None = None,
    db: AsyncSession = Depends(get_db),
) -> List[TrainingJob]:
    """List all training jobs."""
    service = AlgorithmService(db)
    s = TrainingStatus(status) if status else None
    jobs = await service.get_training_jobs(skip=skip, limit=limit, status=s)
    return jobs


@router.post("/predict", response_model=AlgorithmResponse)
async def predict(
    request: AlgorithmRequest,
    db: AsyncSession = Depends(get_db),
) -> AlgorithmResponse:
    """Make a prediction using a trained algorithm."""
    service = AlgorithmService(db)
    
    # For now, return a mock response
    # TODO: Implement actual prediction logic
    return AlgorithmResponse(
        success=True,
        result={
            "prediction": [0.5, 0.3, 0.2],
            "confidence": 0.85,
            "model_used": request.algorithm_type,
        },
        message=f"Prediction using {request.algorithm_type} completed",
    )


@router.get("/available")
async def get_available_algorithms() -> Dict[str, Any]:
    """Get list of available algorithms and their parameters."""
    return {
        "algorithms": [
            {
                "name": "linear_regression",
                "description": "Linear regression for regression tasks",
                "parameters": {
                    "learning_rate": {"type": "float", "default": 0.01},
                    "epochs": {"type": "int", "default": 100},
                },
            },
            {
                "name": "cnn",
                "description": "Convolutional Neural Network for image classification",
                "parameters": {
                    "learning_rate": {"type": "float", "default": 0.001},
                    "epochs": {"type": "int", "default": 10},
                    "batch_size": {"type": "int", "default": 32},
                },
            },
            {
                "name": "transformer",
                "description": "Transformer model for sequence tasks",
                "parameters": {
                    "learning_rate": {"type": "float", "default": 0.0001},
                    "epochs": {"type": "int", "default": 5},
                    "batch_size": {"type": "int", "default": 8},
                },
            },
        ]
    }
