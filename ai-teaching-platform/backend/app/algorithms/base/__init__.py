"""
Base interfaces and exceptions for algorithm implementations.
"""

from app.algorithms.base.interface import (
    BaseTrainer,
    BasePredictor,
    AlgorithmMetadata,
)
from app.algorithms.base.exceptions import (
    AlgorithmError,
    TrainingError,
    PredictionError,
    ModelNotFoundError,
    InvalidParametersError,
    ConfigurationError,
    DatasetError,
    ValidationError,
    ModelSaveError,
    ModelLoadError,
)

__all__ = [
    "BaseTrainer",
    "BasePredictor",
    "AlgorithmMetadata",
    "AlgorithmError",
    "TrainingError",
    "PredictionError",
    "ModelNotFoundError",
    "InvalidParametersError",
    "ConfigurationError",
    "DatasetError",
    "ValidationError",
    "ModelSaveError",
    "ModelLoadError",
]