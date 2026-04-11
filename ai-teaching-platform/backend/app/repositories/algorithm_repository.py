"""
Repository for algorithm-related database operations.
"""
from datetime import datetime
from typing import List, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.algorithm import TrainingJob, ModelMetadata, TrainingStatus
from app.repositories.base_repository import BaseRepository


class AlgorithmRepository:
    """Repository for algorithm entities."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    # TrainingJob operations
    async def create_training_job(self, job_data: dict) -> TrainingJob:
        """Create a new training job."""
        job = TrainingJob(**job_data)
        self.db.add(job)
        await self.db.commit()
        await self.db.refresh(job)
        return job
    
    async def get_training_job(self, job_id: UUID) -> Optional[TrainingJob]:
        """Get a training job by ID."""
        result = await self.db.execute(
            select(TrainingJob).where(TrainingJob.id == job_id)
        )
        return result.scalar_one_or_none()
    
    async def get_training_jobs(
        self, 
        skip: int = 0, 
        limit: int = 100,
        user_id: Optional[UUID] = None,
        status: Optional[TrainingStatus] = None,
    ) -> List[TrainingJob]:
        """Get training jobs with optional filtering."""
        query = select(TrainingJob)
        
        if user_id:
            query = query.where(TrainingJob.user_id == user_id)
        
        if status:
            query = query.where(TrainingJob.status == status)
        
        query = query.order_by(TrainingJob.created_at.desc()).offset(skip).limit(limit)
        
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def update_training_job(
        self, 
        job_id: UUID, 
        update_data: dict
    ) -> Optional[TrainingJob]:
        """Update a training job."""
        job = await self.get_training_job(job_id)
        if not job:
            return None
        
        for key, value in update_data.items():
            if hasattr(job, key):
                setattr(job, key, value)
        
        job.updated_at = datetime.utcnow()
        await self.db.commit()
        await self.db.refresh(job)
        return job
    
    async def delete_training_job(self, job_id: UUID) -> bool:
        """Delete a training job."""
        job = await self.get_training_job(job_id)
        if not job:
            return False
        
        await self.db.delete(job)
        await self.db.commit()
        return True
    
    async def get_running_jobs(self) -> List[TrainingJob]:
        """Get all running training jobs."""
        result = await self.db.execute(
            select(TrainingJob)
            .where(TrainingJob.status == TrainingStatus.RUNNING)
            .order_by(TrainingJob.started_at)
        )
        return result.scalars().all()
    
    async def get_jobs_by_algorithm(
        self, 
        algorithm_type: str,
        skip: int = 0,
        limit: int = 100,
    ) -> List[TrainingJob]:
        """Get training jobs by algorithm type."""
        result = await self.db.execute(
            select(TrainingJob)
            .where(TrainingJob.algorithm_type == algorithm_type)
            .order_by(TrainingJob.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()
    
    # ModelMetadata operations
    async def create_model_metadata(self, metadata_data: dict) -> ModelMetadata:
        """Create new model metadata."""
        metadata = ModelMetadata(**metadata_data)
        self.db.add(metadata)
        await self.db.commit()
        await self.db.refresh(metadata)
        return metadata
    
    async def get_model_metadata(self, metadata_id: UUID) -> Optional[ModelMetadata]:
        """Get model metadata by ID."""
        result = await self.db.execute(
            select(ModelMetadata).where(ModelMetadata.id == metadata_id)
        )
        return result.scalar_one_or_none()
    
    async def get_model_by_training_job(self, job_id: UUID) -> Optional[ModelMetadata]:
        """Get model metadata by training job ID."""
        result = await self.db.execute(
            select(ModelMetadata).where(ModelMetadata.training_job_id == job_id)
        )
        return result.scalar_one_or_none()
    
    async def get_models_by_algorithm(
        self, 
        algorithm_type: str,
        skip: int = 0,
        limit: int = 100,
    ) -> List[ModelMetadata]:
        """Get models by algorithm type."""
        result = await self.db.execute(
            select(ModelMetadata)
            .where(ModelMetadata.algorithm_type == algorithm_type)
            .where(ModelMetadata.is_active == True)
            .order_by(ModelMetadata.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()
    
    async def update_model_metadata(
        self, 
        metadata_id: UUID, 
        update_data: dict
    ) -> Optional[ModelMetadata]:
        """Update model metadata."""
        metadata = await self.get_model_metadata(metadata_id)
        if not metadata:
            return None
        
        for key, value in update_data.items():
            if hasattr(metadata, key):
                setattr(metadata, key, value)
        
        metadata.updated_at = datetime.utcnow()
        await self.db.commit()
        await self.db.refresh(metadata)
        return metadata
    
    async def delete_model_metadata(self, metadata_id: UUID) -> bool:
        """Delete model metadata."""
        metadata = await self.get_model_metadata(metadata_id)
        if not metadata:
            return False
        
        await self.db.delete(metadata)
        await self.db.commit()
        return True