"""
Linear regression predictor implementation.
"""
from typing import Any, Dict, List, Optional

import numpy as np
import torch

from app.algorithms.base.interface import BasePredictor
from app.algorithms.base.exceptions import PredictionError, ModelNotFoundError
from app.algorithms.linear_regression.trainer import LinearRegressionTrainer


class LinearRegressionPredictor(BasePredictor):
    """Linear regression predictor using PyTorch."""
    
    def __init__(self):
        self.trainer = LinearRegressionTrainer()
        self.model = None
    
    def predict(
        self,
        input_data: List[Any],
        model_id: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Make predictions using linear regression.
        
        Args:
            input_data: Input data as list of lists or numpy array
            model_id: Path to saved model file (optional)
            parameters: Prediction parameters
            
        Returns:
            Dictionary with prediction results including:
                - predictions: list of predicted values
                - confidence: optional confidence scores
                - model_used: string indicating model used
        """
        parameters = parameters or {}
        
        try:
            # Load model if specified
            if model_id:
                success = self.trainer.load_model(model_id)
                if not success:
                    raise ModelNotFoundError(f"Model not found at {model_id}")
                self.model = self.trainer.model
            elif self.model is None:
                # Try to use the trainer's model
                self.model = self.trainer.model
                if self.model is None:
                    raise ModelNotFoundError("No model available for prediction")
            
            # Convert input data to tensor
            if isinstance(input_data, list):
                input_tensor = torch.tensor(input_data, dtype=torch.float32)
            elif isinstance(input_data, np.ndarray):
                input_tensor = torch.from_numpy(input_data.astype(np.float32))
            else:
                raise ValueError("input_data must be list or numpy array")
            
            # Check input dimensions
            expected_dim = self.model.in_features
            if input_tensor.shape[-1] != expected_dim:
                # Try to reshape if possible
                if input_tensor.ndim == 1:
                    input_tensor = input_tensor.unsqueeze(-1)
                if input_tensor.shape[-1] != expected_dim:
                    raise ValueError(
                        f"Input dimension mismatch. Expected {expected_dim}, "
                        f"got {input_tensor.shape[-1]}"
                    )
            
            # Make predictions
            self.model.eval()
            with torch.no_grad():
                predictions = self.model(input_tensor)
                predictions_np = predictions.numpy()
            
            # Calculate confidence (for linear regression, we can use prediction interval)
            confidence = self._calculate_confidence(input_tensor, predictions)
            
            return {
                "predictions": predictions_np.tolist(),
                "confidence": confidence,
                "model_used": "linear_regression",
                "input_shape": list(input_tensor.shape),
                "output_shape": list(predictions.shape),
            }
            
        except Exception as e:
            raise PredictionError(f"Linear regression prediction failed: {str(e)}") from e
    
    def evaluate(
        self,
        input_data: List[Any],
        labels: List[Any],
        model_id: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Evaluate linear regression model performance.
        
        Args:
            input_data: Input data
            labels: Ground truth labels
            model_id: Path to saved model file (optional)
            parameters: Evaluation parameters
            
        Returns:
            Dictionary with evaluation metrics including:
                - mse: mean squared error
                - mae: mean absolute error
                - r_squared: R-squared score
                - predictions: list of predicted values
        """
        parameters = parameters or {}
        
        try:
            # Make predictions first
            prediction_result = self.predict(input_data, model_id, parameters)
            predictions = prediction_result["predictions"]
            
            # Convert to numpy arrays
            predictions_np = np.array(predictions)
            labels_np = np.array(labels)
            
            # Ensure shapes match
            if predictions_np.shape != labels_np.shape:
                # Try to reshape if possible
                if predictions_np.size == labels_np.size:
                    predictions_np = predictions_np.reshape(labels_np.shape)
                else:
                    raise ValueError(
                        f"Shape mismatch: predictions {predictions_np.shape}, "
                        f"labels {labels_np.shape}"
                    )
            
            # Calculate metrics
            mse = np.mean((predictions_np - labels_np) ** 2)
            mae = np.mean(np.abs(predictions_np - labels_np))
            
            # Calculate R-squared
            ss_res = np.sum((labels_np - predictions_np) ** 2)
            ss_tot = np.sum((labels_np - np.mean(labels_np)) ** 2)
            r_squared = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0
            
            # Calculate root mean squared error
            rmse = np.sqrt(mse)
            
            # Calculate explained variance
            explained_variance = 1 - np.var(labels_np - predictions_np) / np.var(labels_np)
            
            return {
                "mse": float(mse),
                "mae": float(mae),
                "rmse": float(rmse),
                "r_squared": float(r_squared),
                "explained_variance": float(explained_variance),
                "predictions": predictions_np.tolist(),
                "labels": labels_np.tolist(),
                "sample_count": len(predictions_np),
            }
            
        except Exception as e:
            raise PredictionError(f"Model evaluation failed: {str(e)}") from e
    
    def _calculate_confidence(
        self, 
        input_tensor: torch.Tensor, 
        predictions: torch.Tensor
    ) -> List[float]:
        """
        Calculate confidence scores for predictions.
        
        For linear regression, we can estimate prediction intervals
        based on residual standard error.
        
        Args:
            input_tensor: Input data tensor
            predictions: Prediction tensor
            
        Returns:
            List of confidence scores
        """
        # Simple confidence calculation based on input magnitude
        # In a real implementation, you would use residual analysis
        
        # Use distance from input mean as proxy for confidence
        input_mean = input_tensor.mean(dim=0)
        distances = torch.norm(input_tensor - input_mean, dim=1)
        
        # Normalize distances to [0, 1] range
        max_distance = distances.max()
        if max_distance > 0:
            normalized_distances = distances / max_distance
        else:
            normalized_distances = torch.zeros_like(distances)
        
        # Confidence is inverse of normalized distance
        confidence_scores = 1.0 - normalized_distances.numpy()
        
        # Clip to valid range
        confidence_scores = np.clip(confidence_scores, 0.0, 1.0)
        
        return confidence_scores.tolist()