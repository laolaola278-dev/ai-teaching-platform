"""
Service layer for algorithm engine interactions.
"""
import asyncio
import json
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.algorithm import TrainingJob as TrainingJobModel
from app.repositories.algorithm_repository import AlgorithmRepository
from app.schemas.algorithm import (
    AlgorithmRequest,
    AlgorithmResponse,
    AlgorithmType,
    TrainingJob,
    TrainingJobCreate,
    TrainingRequest,
    TrainingResult,
    TrainingStatus,
)


class AlgorithmService:
    """Service for handling algorithm-related operations."""
    
    def __init__(self, db: AsyncSession):
        self.repository = AlgorithmRepository(db)
    
    async def create_training_job(self, request: AlgorithmRequest) -> TrainingJobModel:
        """Create a new training job record."""
        job_data = TrainingJobCreate(
            algorithm_type=request.algorithm_type,
            parameters=request.parameters,
            status=TrainingStatus.PENDING,
        ).model_dump()
        
        return await self.repository.create_training_job(job_data)
    
    async def get_training_job(self, job_id: UUID) -> Optional[TrainingJobModel]:
        """Get a training job by ID."""
        return await self.repository.get_training_job(job_id)
    
    async def get_training_jobs(
        self, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[TrainingJobModel]:
        """Get a list of training jobs with pagination."""
        return await self.repository.get_training_jobs(skip=skip, limit=limit)
    
    async def update_training_job(
        self, 
        job_id: UUID, 
        update_data: Dict[str, Any]
    ) -> Optional[TrainingJobModel]:
        """Update a training job."""
        return await self.repository.update_training_job(job_id, update_data)
    
    async def execute_training(self, job_id: UUID, request: AlgorithmRequest) -> None:
        """
        Execute training for a job.
        
        This method is designed to be run in a background task.
        """
        # Update job status to running
        await self.update_training_job(job_id, {
            "status": TrainingStatus.RUNNING,
            "started_at": datetime.utcnow(),
            "progress": 10,
        })
        
        try:
            # Import algorithm engine based on type
            if request.algorithm_type == AlgorithmType.LINEAR_REGRESSION:
                from app.algorithms.linear_regression.trainer import LinearRegressionTrainer
                trainer = LinearRegressionTrainer()
            elif request.algorithm_type == AlgorithmType.CNN:
                from app.algorithms.cnn.trainer import CNNTrainer
                trainer = CNNTrainer()
            elif request.algorithm_type == AlgorithmType.TRANSFORMER:
                from app.algorithms.transformer.trainer import TransformerTrainer
                trainer = TransformerTrainer()
            else:
                raise ValueError(f"Unsupported algorithm type: {request.algorithm_type}")
            
            # Simulate training progress updates
            for progress in range(20, 101, 20):
                await asyncio.sleep(1)  # Simulate work
                await self.update_training_job(job_id, {"progress": progress})
            
            # Execute training (mock implementation)
            result = trainer.train(
                parameters=request.parameters,
                config=request.config,
            )
            
            # Update job with results
            await self.update_training_job(job_id, {
                "status": TrainingStatus.COMPLETED,
                "completed_at": datetime.utcnow(),
                "progress": 100,
                "result": TrainingResult(
                    loss_history=result.get("loss_history", []),
                    validation_loss=result.get("validation_loss"),
                    metrics=result.get("metrics", {}),
                    model_path=result.get("model_path"),
                    training_time=result.get("training_time", 0),
                ).model_dump(),
            })
            
        except Exception as e:
            # Update job with error
            await self.update_training_job(job_id, {
                "status": TrainingStatus.FAILED,
                "completed_at": datetime.utcnow(),
                "error_message": str(e),
            })
    
    async def predict(self, request: AlgorithmRequest) -> AlgorithmResponse:
        """Make predictions using an algorithm."""
        try:
            # Import appropriate predictor based on algorithm type
            if request.algorithm_type == AlgorithmType.LINEAR_REGRESSION:
                from app.algorithms.linear_regression.predictor import LinearRegressionPredictor
                predictor = LinearRegressionPredictor()
            elif request.algorithm_type == AlgorithmType.CNN:
                from app.algorithms.cnn.predictor import CNNPredictor
                predictor = CNNPredictor()
            elif request.algorithm_type == AlgorithmType.TRANSFORMER:
                from app.algorithms.transformer.predictor import TransformerPredictor
                predictor = TransformerPredictor()
            else:
                return AlgorithmResponse(
                    success=False,
                    error=f"Unsupported algorithm type: {request.algorithm_type}",
                )
            
            # Make prediction (mock implementation)
            result = predictor.predict(
                input_data=request.parameters.get("input_data", []),
                model_id=request.parameters.get("model_id"),
            )
            
            return AlgorithmResponse(
                success=True,
                result=result,
                message=f"Prediction using {request.algorithm_type} completed",
            )
            
        except Exception as e:
            return AlgorithmResponse(
                success=False,
                error=str(e),
                message=f"Prediction failed: {e}",
            )