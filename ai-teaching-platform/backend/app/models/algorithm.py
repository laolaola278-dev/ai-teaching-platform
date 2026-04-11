"""
SQLAlchemy models for algorithm training jobs and model metadata.
"""
import enum
from typing import TYPE_CHECKING, Optional

from sqlalchemy import JSON, Boolean, Enum, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel, TimestampMixin

if TYPE_CHECKING:
    from app.models.user import User


class AlgorithmType(enum.Enum):
    """Supported algorithm types."""
    LINEAR_REGRESSION = "linear_regression"
    CNN = "cnn"
    TRANSFORMER = "transformer"


class TrainingStatus(enum.Enum):
    """Status of a training job."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TrainingJob(BaseModel, TimestampMixin):
    """Training job model for tracking algorithm training."""
    
    __tablename__ = "training_jobs"
    
    # Columns
    algorithm_type: Mapped[AlgorithmType] = mapped_column(
        Enum(AlgorithmType),
        nullable=False,
        index=True,
    )
    parameters: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    status: Mapped[TrainingStatus] = mapped_column(
        Enum(TrainingStatus),
        nullable=False,
        default=TrainingStatus.PENDING,
        index=True,
    )
    progress: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    started_at: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    completed_at: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    
    # Result columns
    loss_history: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    validation_loss: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    metrics: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    model_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    training_time: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    # Foreign keys
    user_id: Mapped[Optional[str]] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    
    # Relationships
    user: Mapped[Optional["User"]] = relationship("User", back_populates="training_jobs")
    model_metadata: Mapped[Optional["ModelMetadata"]] = relationship(
        "ModelMetadata", 
        back_populates="training_job",
        uselist=False,
        cascade="all, delete-orphan",
    )
    
    def __repr__(self) -> str:
        return f"<TrainingJob(id={self.id}, algorithm_type={self.algorithm_type}, status={self.status})>"


class ModelMetadata(BaseModel, TimestampMixin):
    """Model metadata for trained algorithms."""
    
    __tablename__ = "model_metadata"
    
    # Columns
    name: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    algorithm_type: Mapped[AlgorithmType] = mapped_column(
        Enum(AlgorithmType),
        nullable=False,
        index=True,
    )
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    version: Mapped[str] = mapped_column(String(20), nullable=False, default="1.0.0")
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    file_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    file_size: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    # Foreign keys
    training_job_id: Mapped[Optional[str]] = mapped_column(
        ForeignKey("training_jobs.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        unique=True,
    )
    
    # Relationships
    training_job: Mapped[Optional["TrainingJob"]] = relationship(
        "TrainingJob", 
        back_populates="model_metadata",
    )
    
    def __repr__(self) -> str:
        return f"<ModelMetadata(id={self.id}, name='{self.name}', algorithm_type={self.algorithm_type})>"