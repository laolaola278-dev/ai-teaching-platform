"""Predictor for Linear Regression (skeleton)."""
from __future__ import annotations
from typing import List, Any

import numpy as np


class LinearRegressionPredictor:
    def __init__(self):
        self.coef_ = None
        self.intercept_ = 0.0

    def predict(self, input_data: List[List[float]], model_id: str | None = None) -> dict:
        X = np.array(input_data, dtype=float)
        if self.coef_ is None:
            # No model loaded; return zeros
            preds = np.zeros(X.shape[0]).tolist()
        else:
            preds = (X @ self.coef_ + self.intercept_).tolist()
        return {"predictions": preds}
