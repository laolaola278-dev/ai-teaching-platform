"""Abstract base trainer for algorithm engines."""
from __future__ import annotations

from abc import ABC, abstractmethod

class BaseTrainer(ABC):
    @abstractmethod
    def train(self, parameters: dict, config: dict) -> dict:
        """Train a model and return a result dict."""
        raise NotImplementedError
