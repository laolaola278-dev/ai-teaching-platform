"""
CNN algorithm implementation for image classification.
"""

from app.algorithms.cnn.trainer import CNNTrainer, SimpleCNN
from app.algorithms.cnn.predictor import CNNPredictor

__all__ = [
    "CNNTrainer",
    "SimpleCNN",
    "CNNPredictor",
]