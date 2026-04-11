"""
Pydantic models for algorithm engine interactions.
"""
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


# Enums
class AlgorithmType(str, Enum):
    """Supported algorithm types."""
    LINEAR_REGRESSION = "linear_regression"
    CNN = "cnn"
    TRANSFORMER = "transformer"


class TrainingStatus(str, Enum):
    """Status of a training job."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


# Request schemas
class AlgorithmRequest(BaseModel):
    """Base request schema for algorithm operations."""
    algorithm_type: AlgorithmType
    parameters: Dict[str, Any] = Field(default_factory=dict)
    dataset_id: Optional[str] = Field(None, description="ID of dataset to use")
    config: Dict[str, Any] = Field(default_factory=dict)


class TrainingRequest(AlgorithmRequest):
    """Request schema for starting a training job."""
    epochs: int = Field(default=10, ge=1)
    batch_size: int = Field(default=32, ge=1)
    learning_rate: float = Field(default=0.001, gt=0)
    validation_split: float = Field(default=0.2, ge=0, le=1)


class PredictionRequest(BaseModel):
    """Request schema for making predictions."""
    algorithm_type: AlgorithmType
    model_id: Optional[str] = Field(None, description="ID of trained model to use")
    input_data: List[Any] = Field(..., description="Input data for prediction")
    parameters: Dict[str, Any] = Field(default_factory=dict)


# Response schemas
class AlgorithmResponse(BaseModel):
    """Base response schema for algorithm operations."""
    success: bool
    result: Dict[str, Any] = Field(default_factory=dict)
    message: str = ""
    error: Optional[str] = None


class TrainingResult(BaseModel):
    """Schema for training results."""
    loss_history: List[float] = Field(default_factory=list)
    validation_loss: Optional[List[float]] = None
    metrics: Dict[str, float] = Field(default_factory=dict)
    model_path: Optional[str] = None
    training_time: float = Field(0, description="Training time in seconds")


class PredictionResult(BaseModel):
    """Schema for prediction results."""
    predictions: List[Any] = Field(default_factory=list)
    probabilities: Optional[List[List[float]]] = None
    confidence: Optional[float] = None
    model_used: str


# Job tracking schemas
class TrainingJobBase(BaseModel):
    """Base training job schema."""
    algorithm_type: AlgorithmType
    parameters: Dict[str, Any] = Field(default_factory=dict)
    status: TrainingStatus = TrainingStatus.PENDING
    progress: float = Field(default=0, ge=0, le=100)
    error_message: Optional[str] = None


class TrainingJobCreate(TrainingJobBase):
    """Schema for creating a training job."""
    user_id: Optional[UUID] = None


class TrainingJobUpdate(BaseModel):
    """Schema for updating a training job."""
    status: Optional[TrainingStatus] = None
    progress: Optional[float] = Field(None, ge=0, le=100)
    error_message: Optional[str] = None
    result: Optional[TrainingResult] = None


class TrainingJob(TrainingJobBase):
    """Schema for returning a training job."""
    id: UUID
    user_id: Optional[UUID]
    created_at: datetime
    updated_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result: Optional[TrainingResult] = None
    
    class Config:
        from_attributes = True


# Model metadata schemas
class ModelMetadataBase(BaseModel):
    """Base model metadata schema."""
    name: str = Field(..., min_length=1, max_length=200)
    algorithm_type: AlgorithmType
    description: Optional[str] = Field(None, max_length=2000)
    version: str = Field(default="1.0.0")
    is_active: bool = Field(default=True)


class ModelMetadataCreate(ModelMetadataBase):
    """Schema for creating model metadata."""
    training_job_id: Optional[UUID] = None


class ModelMetadata(ModelMetadataBase):
    """Schema for returning model metadata."""
    id: UUID
    training_job_id: Optional[UUID]
    created_at: datetime
    updated_at: datetime
    file_path: Optional[str] = None
    file_size: Optional[int] = None
    
    class Config:
        from_attributes = True