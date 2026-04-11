"""
SQLAlchemy models for the AI Teaching Platform.
"""

from app.models.base import BaseModel, TimestampMixin
from app.models.course import Course, Chapter, Notebook
from app.models.user import User, Role, Permission, UserCourseProgress
from app.models.algorithm import TrainingJob, ModelMetadata, AlgorithmType, TrainingStatus

__all__ = [
    "BaseModel",
    "TimestampMixin",
    "Course",
    "Chapter",
    "Notebook",
    "User",
    "Role",
    "Permission",
    "UserCourseProgress",
    "TrainingJob",
    "ModelMetadata",
    "AlgorithmType",
    "TrainingStatus",
]