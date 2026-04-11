"""
Algorithm engine implementations for the AI Teaching Platform.
"""

from app.algorithms.base import *
from app.algorithms.linear_regression import *
from app.algorithms.cnn import *
from app.algorithms.transformer import *

__all__ = [
    # Base
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
    
    # Linear Regression
    "LinearRegressionTrainer",
    "LinearRegressionPredictor",
    
    # CNN
    "CNNTrainer",
    "SimpleCNN",
    "CNNPredictor",
    
    # Transformer
    "TransformerTrainer",
    "SimpleTransformer",
    "TransformerPredictor",
]