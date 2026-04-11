"""
Linear regression trainer implementation.

This module provides a PyTorch-based linear regression trainer
following the educational style of fastbook examples.
"""
import time
from typing import Any, Dict, Optional

import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset

from app.algorithms.base.interface import BaseTrainer
from app.algorithms.base.exceptions import TrainingError, ValidationError


class LinearRegressionTrainer(BaseTrainer):
    """Linear regression trainer using PyTorch."""
    
    def __init__(self):
        self.model = None
        self.training_history = {
            "loss_history": [],
            "val_loss_history": [],
            "epoch_times": [],
        }
    
    def train(
        self,
        parameters: Dict[str, Any],
        config: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Train a linear regression model.
        
        Args:
            parameters: Training parameters including:
                - learning_rate: float, learning rate for optimizer
                - epochs: int, number of training epochs
                - batch_size: int, batch size for training
                - input_dim: int, input dimension
                - output_dim: int, output dimension
                - train_data: optional, training data as (X, y) tuple
                - val_data: optional, validation data as (X, y) tuple
            config: Additional configuration
            
        Returns:
            Dictionary with training results including:
                - loss_history: list of training losses
                - val_loss_history: list of validation losses
                - final_loss: float, final training loss
                - final_val_loss: float, final validation loss
                - training_time: float, total training time in seconds
                - model_summary: dict, model architecture summary
        """
        config = config or {}
        
        try:
            # Extract parameters with defaults
            learning_rate = parameters.get("learning_rate", 0.01)
            epochs = parameters.get("epochs", 100)
            batch_size = parameters.get("batch_size", 32)
            input_dim = parameters.get("input_dim", 1)
            output_dim = parameters.get("output_dim", 1)
            
            # Generate or use provided data
            train_data = parameters.get("train_data")
            val_data = parameters.get("val_data")
            
            if train_data is None:
                # Generate synthetic data for demonstration
                train_data = self._generate_synthetic_data(
                    n_samples=1000,
                    input_dim=input_dim,
                    output_dim=output_dim,
                )
            
            if val_data is None:
                val_data = self._generate_synthetic_data(
                    n_samples=200,
                    input_dim=input_dim,
                    output_dim=output_dim,
                )
            
            # Prepare data loaders
            train_loader = self._prepare_data_loader(train_data, batch_size, shuffle=True)
            val_loader = self._prepare_data_loader(val_data, batch_size, shuffle=False)
            
            # Initialize model
            self.model = nn.Linear(input_dim, output_dim)
            
            # Loss function and optimizer
            criterion = nn.MSELoss()
            optimizer = optim.SGD(self.model.parameters(), lr=learning_rate)
            
            # Training loop
            start_time = time.time()
            self.training_history = {
                "loss_history": [],
                "val_loss_history": [],
                "epoch_times": [],
            }
            
            for epoch in range(epochs):
                epoch_start = time.time()
                
                # Training phase
                self.model.train()
                train_loss = 0.0
                
                for X_batch, y_batch in train_loader:
                    optimizer.zero_grad()
                    predictions = self.model(X_batch)
                    loss = criterion(predictions, y_batch)
                    loss.backward()
                    optimizer.step()
                    train_loss += loss.item()
                
                avg_train_loss = train_loss / len(train_loader)
                self.training_history["loss_history"].append(avg_train_loss)
                
                # Validation phase
                val_loss = self._evaluate_model(val_loader, criterion)
                self.training_history["val_loss_history"].append(val_loss)
                
                epoch_time = time.time() - epoch_start
                self.training_history["epoch_times"].append(epoch_time)
                
                # Log progress every 10 epochs
                if (epoch + 1) % 10 == 0:
                    print(f"Epoch {epoch + 1}/{epochs} - "
                          f"Train Loss: {avg_train_loss:.4f}, "
                          f"Val Loss: {val_loss:.4f}, "
                          f"Time: {epoch_time:.2f}s")
            
            total_time = time.time() - start_time
            
            # Prepare results
            results = {
                "loss_history": self.training_history["loss_history"],
                "validation_loss": self.training_history["val_loss_history"],
                "training_time": total_time,
                "model_summary": {
                    "input_dim": input_dim,
                    "output_dim": output_dim,
                    "parameters": sum(p.numel() for p in self.model.parameters()),
                    "trainable_parameters": sum(p.numel() for p in self.model.parameters() if p.requires_grad),
                },
                "final_loss": self.training_history["loss_history"][-1],
                "final_val_loss": self.training_history["val_loss_history"][-1],
                "epoch_times": self.training_history["epoch_times"],
            }
            
            return results
            
        except Exception as e:
            raise TrainingError(f"Linear regression training failed: {str(e)}") from e
    
    def validate(
        self,
        parameters: Dict[str, Any],
        config: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Validate the trained linear regression model."""
        if self.model is None:
            raise ValidationError("Model not trained. Call train() first.")
        
        config = config or {}
        
        try:
            # Extract validation data
            val_data = parameters.get("val_data")
            if val_data is None:
                input_dim = self.model.in_features
                output_dim = self.model.out_features
                val_data = self._generate_synthetic_data(
                    n_samples=200,
                    input_dim=input_dim,
                    output_dim=output_dim,
                )
            
            # Prepare data loader
            batch_size = parameters.get("batch_size", 32)
            val_loader = self._prepare_data_loader(val_data, batch_size, shuffle=False)
            
            # Evaluate model
            criterion = nn.MSELoss()
            val_loss = self._evaluate_model(val_loader, criterion)
            
            # Calculate R-squared score
            self.model.eval()
            all_predictions = []
            all_targets = []
            
            with torch.no_grad():
                for X_batch, y_batch in val_loader:
                    predictions = self.model(X_batch)
                    all_predictions.append(predictions.numpy())
                    all_targets.append(y_batch.numpy())
            
            predictions_np = np.concatenate(all_predictions)
            targets_np = np.concatenate(all_targets)
            
            # Calculate R-squared
            ss_res = np.sum((targets_np - predictions_np) ** 2)
            ss_tot = np.sum((targets_np - np.mean(targets_np)) ** 2)
            r_squared = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0
            
            return {
                "validation_loss": val_loss,
                "r_squared": float(r_squared),
                "predictions": predictions_np.tolist(),
                "targets": targets_np.tolist(),
            }
            
        except Exception as e:
            raise ValidationError(f"Model validation failed: {str(e)}") from e
    
    def save_model(self, path: str) -> bool:
        """Save the trained model to disk."""
        if self.model is None:
            raise ModelSaveError("No model to save. Train a model first.")
        
        try:
            torch.save({
                "model_state_dict": self.model.state_dict(),
                "training_history": self.training_history,
                "model_config": {
                    "input_dim": self.model.in_features,
                    "output_dim": self.model.out_features,
                },
            }, path)
            return True
        except Exception as e:
            raise ModelSaveError(f"Failed to save model: {str(e)}") from e
    
    def load_model(self, path: str) -> bool:
        """Load a trained model from disk."""
        try:
            checkpoint = torch.load(path)
            
            input_dim = checkpoint["model_config"]["input_dim"]
            output_dim = checkpoint["model_config"]["output_dim"]
            
            self.model = nn.Linear(input_dim, output_dim)
            self.model.load_state_dict(checkpoint["model_state_dict"])
            self.training_history = checkpoint["training_history"]
            
            return True
        except Exception as e:
            raise ModelLoadError(f"Failed to load model: {str(e)}") from e
    
    # Helper methods
    def _generate_synthetic_data(
        self, 
        n_samples: int, 
        input_dim: int, 
        output_dim: int
    ) -> tuple:
        """Generate synthetic linear regression data."""
        # Generate random input
        X = torch.randn(n_samples, input_dim)
        
        # Generate true weights and bias
        true_weights = torch.randn(input_dim, output_dim)
        true_bias = torch.randn(output_dim)
        
        # Generate targets with some noise
        y = X @ true_weights + true_bias
        y += 0.1 * torch.randn_like(y)  # Add noise
        
        return X, y
    
    def _prepare_data_loader(
        self, 
        data: tuple, 
        batch_size: int, 
        shuffle: bool
    ) -> DataLoader:
        """Prepare a PyTorch DataLoader from data tuple."""
        X, y = data
        dataset = TensorDataset(X, y)
        return DataLoader(dataset, batch_size=batch_size, shuffle=shuffle)
    
    def _evaluate_model(self, data_loader: DataLoader, criterion) -> float:
        """Evaluate model on data loader."""
        if self.model is None:
            return float("inf")
        
        self.model.eval()
        total_loss = 0.0
        
        with torch.no_grad():
            for X_batch, y_batch in data_loader:
                predictions = self.model(X_batch)
                loss = criterion(predictions, y_batch)
                total_loss += loss.item()
        
        return total_loss / len(data_loader)