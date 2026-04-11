"""
CNN predictor implementation for image classification.
"""
from typing import Any, Dict, List, Optional

import numpy as np
import torch
import torch.nn.functional as F

from app.algorithms.base.interface import BasePredictor
from app.algorithms.base.exceptions import PredictionError, ModelNotFoundError
from app.algorithms.cnn.trainer import CNNTrainer, SimpleCNN


class CNNPredictor(BasePredictor):
    """CNN predictor for image classification tasks."""
    
    def __init__(self):
        self.trainer = CNNTrainer()
        self.model = None
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    
    def predict(
        self,
        input_data: List[Any],
        model_id: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Make predictions using CNN.
        
        Args:
            input_data: Input images as list of numpy arrays or tensors
            model_id: Path to saved model file (optional)
            parameters: Prediction parameters including:
                - input_channels: int, number of input channels
                - image_size: tuple, expected image size
        
        Returns:
            Dictionary with prediction results
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
            input_tensor = self._prepare_input(input_data, parameters)
            
            # Check input dimensions
            expected_channels = self.model.conv1.in_channels
            if input_tensor.shape[1] != expected_channels:
                raise ValueError(
                    f"Input channel mismatch. Expected {expected_channels}, "
                    f"got {input_tensor.shape[1]}"
                )
            
            # Make predictions
            self.model.eval()
            with torch.no_grad():
                input_tensor = input_tensor.to(self.device)
                outputs = self.model(input_tensor)
                probabilities = F.softmax(outputs, dim=1)
                _, predictions = torch.max(outputs, 1)
                
                # Convert to numpy
                predictions_np = predictions.cpu().numpy()
                probabilities_np = probabilities.cpu().numpy()
            
            # Get class labels and confidence
            confidence_scores = np.max(probabilities_np, axis=1)
            predicted_classes = predictions_np.tolist()
            
            # Get top-k predictions
            top_k = parameters.get("top_k", 3)
            top_k_probs, top_k_indices = torch.topk(probabilities, k=top_k, dim=1)
            top_k_probs_np = top_k_probs.cpu().numpy()
            top_k_indices_np = top_k_indices.cpu().numpy()
            
            # Format results
            results = []
            for i in range(len(predicted_classes)):
                top_k_list = []
                for j in range(top_k):
                    top_k_list.append({
                        "class": int(top_k_indices_np[i][j]),
                        "probability": float(top_k_probs_np[i][j]),
                    })
                
                results.append({
                    "predicted_class": predicted_classes[i],
                    "confidence": float(confidence_scores[i]),
                    "probabilities": probabilities_np[i].tolist(),
                    "top_k": top_k_list,
                })
            
            return {
                "predictions": results,
                "model_used": "cnn",
                "input_shape": list(input_tensor.shape),
                "device_used": str(self.device),
                "num_classes": self.model.fc3.out_features,
            }
            
        except Exception as e:
            raise PredictionError(f"CNN prediction failed: {str(e)}") from e
    
    def evaluate(
        self,
        input_data: List[Any],
        labels: List[Any],
        model_id: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Evaluate CNN model performance.
        
        Args:
            input_data: Input images
            labels: Ground truth labels
            model_id: Path to saved model file (optional)
            parameters: Evaluation parameters
            
        Returns:
            Dictionary with evaluation metrics
        """
        parameters = parameters or {}
        
        try:
            # Make predictions first
            prediction_result = self.predict(input_data, model_id, parameters)
            predictions = prediction_result["predictions"]
            
            # Extract predicted classes
            predicted_classes = [pred["predicted_class"] for pred in predictions]
            
            # Convert to numpy arrays
            predictions_np = np.array(predicted_classes)
            labels_np = np.array(labels)
            
            # Ensure shapes match
            if predictions_np.shape != labels_np.shape:
                raise ValueError(
                    f"Shape mismatch: predictions {predictions_np.shape}, "
                    f"labels {labels_np.shape}"
                )
            
            # Calculate metrics
            accuracy = np.mean(predictions_np == labels_np)
            
            # Calculate per-class metrics
            unique_classes = np.unique(np.concatenate([predictions_np, labels_np]))
            per_class_metrics = {}
            
            for cls in unique_classes:
                # Precision, recall, F1 for this class
                true_pos = np.sum((predictions_np == cls) & (labels_np == cls))
                false_pos = np.sum((predictions_np == cls) & (labels_np != cls))
                false_neg = np.sum((predictions_np != cls) & (labels_np == cls))
                
                precision = true_pos / (true_pos + false_pos) if (true_pos + false_pos) > 0 else 0
                recall = true_pos / (true_pos + false_neg) if (true_pos + false_neg) > 0 else 0
                f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0
                
                per_class_metrics[int(cls)] = {
                    "precision": float(precision),
                    "recall": float(recall),
                    "f1_score": float(f1),
                    "support": int(np.sum(labels_np == cls)),
                }
            
            # Calculate confusion matrix
            confusion_matrix = {}
            for true_cls in unique_classes:
                for pred_cls in unique_classes:
                    key = f"{true_cls}_{pred_cls}"
                    confusion_matrix[key] = int(
                        np.sum((labels_np == true_cls) & (predictions_np == pred_cls))
                    )
            
            # Calculate macro and weighted averages
            precisions = [metrics["precision"] for metrics in per_class_metrics.values()]
            recalls = [metrics["recall"] for metrics in per_class_metrics.values()]
            f1_scores = [metrics["f1_score"] for metrics in per_class_metrics.values()]
            supports = [metrics["support"] for metrics in per_class_metrics.values()]
            
            macro_precision = np.mean(precisions)
            macro_recall = np.mean(recalls)
            macro_f1 = np.mean(f1_scores)
            
            weighted_precision = np.average(precisions, weights=supports)
            weighted_recall = np.average(recalls, weights=supports)
            weighted_f1 = np.average(f1_scores, weights=supports)
            
            return {
                "accuracy": float(accuracy),
                "per_class_metrics": per_class_metrics,
                "confusion_matrix": confusion_matrix,
                "macro_precision": float(macro_precision),
                "macro_recall": float(macro_recall),
                "macro_f1": float(macro_f1),
                "weighted_precision": float(weighted_precision),
                "weighted_recall": float(weighted_recall),
                "weighted_f1": float(weighted_f1),
                "predictions": predicted_classes,
                "labels": labels_np.tolist(),
                "sample_count": len(predictions_np),
            }
            
        except Exception as e:
            raise PredictionError(f"Model evaluation failed: {str(e)}") from e
    
    def _prepare_input(
        self, 
        input_data: List[Any], 
        parameters: Dict[str, Any]
    ) -> torch.Tensor:
        """Prepare input data as tensor."""
        # Handle different input formats
        if isinstance(input_data, list):
            # Convert list of arrays to tensor
            if all(isinstance(item, np.ndarray) for item in input_data):
                input_arrays = [item.astype(np.float32) for item in input_data]
                input_tensor = torch.tensor(np.stack(input_arrays))
            elif all(isinstance(item, list) for item in input_data):
                # Nested list
                input_tensor = torch.tensor(input_data, dtype=torch.float32)
            else:
                # Assume it's already in tensor format
                input_tensor = torch.tensor(input_data, dtype=torch.float32)
        elif isinstance(input_data, np.ndarray):
            input_tensor = torch.from_numpy(input_data.astype(np.float32))
        elif isinstance(input_data, torch.Tensor):
            input_tensor = input_data.float()
        else:
            raise ValueError(f"Unsupported input type: {type(input_data)}")
        
        # Ensure correct shape: (batch, channels, height, width)
        if input_tensor.ndim == 3:
            # Assume (channels, height, width) -> add batch dimension
            input_tensor = input_tensor.unsqueeze(0)
        elif input_tensor.ndim == 4:
            # Already (batch, channels, height, width)
            pass
        else:
            raise ValueError(
                f"Input must be 3D or 4D tensor, got {input_tensor.ndim}D"
            )
        
        # Normalize if needed
        if parameters.get("normalize", True):
            # Simple normalization to [0, 1]
            input_tensor = input_tensor / 255.0 if input_tensor.max() > 1 else input_tensor
        
        return input_tensor