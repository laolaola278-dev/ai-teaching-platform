"""
Transformer predictor implementation for sequence tasks.
"""
from typing import Any, Dict, List, Optional

import numpy as np
import torch
import torch.nn.functional as F

from app.algorithms.base.interface import BasePredictor
from app.algorithms.base.exceptions import PredictionError, ModelNotFoundError
from app.algorithms.transformer.trainer import TransformerTrainer, SimpleTransformer


class TransformerPredictor(BasePredictor):
    """Transformer predictor for sequence tasks."""
    
    def __init__(self):
        self.trainer = TransformerTrainer()
        self.model = None
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    
    def predict(
        self,
        input_data: List[Any],
        model_id: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Make predictions using Transformer.
        
        Args:
            input_data: Input sequences as list of token lists
            model_id: Path to saved model file (optional)
            parameters: Prediction parameters including:
                - vocab_size: int, vocabulary size
                - max_seq_length: int, maximum sequence length
                - num_classes: int, number of output classes
        
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
            expected_vocab_size = self.model.vocab_size
            # Note: We don't validate vocab size here since embeddings handle OOV
            
            # Make predictions
            self.model.eval()
            with torch.no_grad():
                input_tensor = input_tensor.to(self.device)
                outputs = self.model(input_tensor)
                
                # For classification, get probabilities
                if self.model.fc_out.out_features > 1:
                    probabilities = F.softmax(outputs, dim=1)
                    _, predictions = torch.max(outputs, 1)
                    
                    # Convert to numpy
                    predictions_np = predictions.cpu().numpy()
                    probabilities_np = probabilities.cpu().numpy()
                    
                    # Get confidence scores
                    confidence_scores = np.max(probabilities_np, axis=1)
                    
                    # Get top-k predictions
                    top_k = parameters.get("top_k", 3)
                    top_k_probs, top_k_indices = torch.topk(probabilities, k=top_k, dim=1)
                    top_k_probs_np = top_k_probs.cpu().numpy()
                    top_k_indices_np = top_k_indices.cpu().numpy()
                    
                    # Format results
                    results = []
                    for i in range(len(predictions_np)):
                        top_k_list = []
                        for j in range(top_k):
                            top_k_list.append({
                                "class": int(top_k_indices_np[i][j]),
                                "probability": float(top_k_probs_np[i][j]),
                            })
                        
                        results.append({
                            "predicted_class": int(predictions_np[i]),
                            "confidence": float(confidence_scores[i]),
                            "probabilities": probabilities_np[i].tolist(),
                            "top_k": top_k_list,
                        })
                    
                    result_type = "classification"
                else:
                    # Regression task
                    predictions_np = outputs.cpu().numpy()
                    
                    results = []
                    for i in range(len(predictions_np)):
                        results.append({
                            "prediction": float(predictions_np[i][0]),
                        })
                    
                    result_type = "regression"
            
            return {
                "predictions": results,
                "model_used": "transformer",
                "result_type": result_type,
                "input_shape": list(input_tensor.shape),
                "device_used": str(self.device),
                "num_classes": self.model.fc_out.out_features,
            }
            
        except Exception as e:
            raise PredictionError(f"Transformer prediction failed: {str(e)}") from e
    
    def evaluate(
        self,
        input_data: List[Any],
        labels: List[Any],
        model_id: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Evaluate Transformer model performance.
        
        Args:
            input_data: Input sequences
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
            
            # Check if classification or regression
            if prediction_result["result_type"] == "classification":
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
                
                # Calculate classification metrics
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
                    "task_type": "classification",
                }
            
            else:
                # Regression task
                predicted_values = [pred["prediction"] for pred in predictions]
                
                # Convert to numpy arrays
                predictions_np = np.array(predicted_values)
                labels_np = np.array(labels).astype(np.float32)
                
                # Ensure shapes match
                if predictions_np.shape != labels_np.shape:
                    # Try to flatten
                    predictions_np = predictions_np.flatten()
                    labels_np = labels_np.flatten()
                    
                    if predictions_np.shape != labels_np.shape:
                        raise ValueError(
                            f"Shape mismatch: predictions {predictions_np.shape}, "
                            f"labels {labels_np.shape}"
                        )
                
                # Calculate regression metrics
                mse = np.mean((predictions_np - labels_np) ** 2)
                mae = np.mean(np.abs(predictions_np - labels_np))
                rmse = np.sqrt(mse)
                
                # Calculate R-squared
                ss_res = np.sum((labels_np - predictions_np) ** 2)
                ss_tot = np.sum((labels_np - np.mean(labels_np)) ** 2)
                r_squared = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0
                
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
                    "task_type": "regression",
                }
            
        except Exception as e:
            raise PredictionError(f"Model evaluation failed: {str(e)}") from e
    
    def _prepare_input(
        self, 
        input_data: List[Any], 
        parameters: Dict[str, Any]
    ) -> torch.Tensor:
        """Prepare input sequences as tensor."""
        # Handle different input formats
        if isinstance(input_data, list):
            if all(isinstance(item, list) for item in input_data):
                # List of token lists
                max_len = parameters.get("max_seq_length", 512)
                
                # Pad sequences
                padded_sequences = []
                for seq in input_data:
                    if len(seq) > max_len:
                        seq = seq[:max_len]
                    else:
                        # Pad with zeros
                        pad_len = max_len - len(seq)
                        seq = seq + [0] * pad_len
                    padded_sequences.append(seq)
                
                input_tensor = torch.tensor(padded_sequences, dtype=torch.long)
            
            elif all(isinstance(item, (int, np.integer)) for item in input_data):
                # Single sequence of tokens
                max_len = parameters.get("max_seq_length", 512)
                seq = input_data
                
                if len(seq) > max_len:
                    seq = seq[:max_len]
                else:
                    pad_len = max_len - len(seq)
                    seq = seq + [0] * pad_len
                
                input_tensor = torch.tensor([seq], dtype=torch.long)
            
            else:
                # Assume it's already in tensor format
                input_tensor = torch.tensor(input_data, dtype=torch.long)
        
        elif isinstance(input_data, np.ndarray):
            input_tensor = torch.from_numpy(input_data.astype(np.int64))
        
        elif isinstance(input_data, torch.Tensor):
            input_tensor = input_data.long()
        
        else:
            raise ValueError(f"Unsupported input type: {type(input_data)}")
        
        # Ensure correct shape: (batch_size, seq_length)
        if input_tensor.ndim == 1:
            # Single sequence -> add batch dimension
            input_tensor = input_tensor.unsqueeze(0)
        elif input_tensor.ndim == 2:
            # Already (batch_size, seq_length)
            pass
        else:
            raise ValueError(
                f"Input must be 1D or 2D tensor, got {input_tensor.ndim}D"
            )
        
        return input_tensor