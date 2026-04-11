"""
Transformer trainer implementation for sequence tasks.

This module provides a Transformer trainer inspired by the
llm-from-scratch implementation.
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


class SimpleTransformer(nn.Module):
    """Simple Transformer model for sequence classification/regression."""
    
    def __init__(
        self,
        vocab_size: int = 1000,
        d_model: int = 512,
        nhead: int = 8,
        num_encoder_layers: int = 6,
        num_decoder_layers: int = 6,
        dim_feedforward: int = 2048,
        max_seq_length: int = 512,
        num_classes: int = 10,
        dropout: float = 0.1,
    ):
        super().__init__()
        
        self.d_model = d_model
        self.vocab_size = vocab_size
        self.max_seq_length = max_seq_length
        
        # Embedding layer
        self.embedding = nn.Embedding(vocab_size, d_model)
        
        # Positional encoding
        self.positional_encoding = self._create_positional_encoding(max_seq_length, d_model)
        
        # Transformer encoder
        encoder_layer = nn.TransformerEncoderLayer(
            d_model=d_model,
            nhead=nhead,
            dim_feedforward=dim_feedforward,
            dropout=dropout,
            activation="relu",
            batch_first=True,
        )
        self.transformer_encoder = nn.TransformerEncoder(
            encoder_layer,
            num_layers=num_encoder_layers,
        )
        
        # Output layer
        self.fc_out = nn.Linear(d_model, num_classes)
        
        # Dropout
        self.dropout = nn.Dropout(dropout)
        
        # Initialize weights
        self._init_weights()
    
    def _create_positional_encoding(self, max_len: int, d_model: int) -> torch.Tensor:
        """Create sinusoidal positional encodings."""
        position = torch.arange(max_len).unsqueeze(1)
        div_term = torch.exp(torch.arange(0, d_model, 2) * (-np.log(10000.0) / d_model))
        
        pe = torch.zeros(max_len, d_model)
        pe[:, 0::2] = torch.sin(position * div_term)
        pe[:, 1::2] = torch.cos(position * div_term)
        
        return pe  # (max_len, d_model)
    
    def _init_weights(self):
        """Initialize model weights."""
        for p in self.parameters():
            if p.dim() > 1:
                nn.init.xavier_uniform_(p)
    
    def forward(self, x, attention_mask=None):
        """
        Forward pass.
        
        Args:
            x: Input tensor of shape (batch_size, seq_length)
            attention_mask: Optional attention mask
            
        Returns:
            Output tensor of shape (batch_size, num_classes)
        """
        batch_size, seq_length = x.shape
        
        # Embedding
        x = self.embedding(x) * np.sqrt(self.d_model)
        
        # Add positional encoding
        if seq_length <= self.max_seq_length:
            x = x + self.positional_encoding[:seq_length].to(x.device)
        else:
            # Handle sequences longer than max_seq_length
            x = x + self.positional_encoding[-seq_length:].to(x.device)
        
        # Apply dropout
        x = self.dropout(x)
        
        # Create padding mask if needed
        src_mask = None
        if attention_mask is not None:
            # Convert attention mask to transformer format
            src_key_padding_mask = (attention_mask == 0)
        else:
            src_key_padding_mask = None
        
        # Transformer encoder
        x = self.transformer_encoder(
            x,
            mask=src_mask,
            src_key_padding_mask=src_key_padding_mask,
        )
        
        # Pooling: use the output corresponding to the first token
        x = x[:, 0, :]  # (batch_size, d_model)
        
        # Output layer
        x = self.fc_out(x)
        
        return x


class TransformerTrainer(BaseTrainer):
    """Transformer trainer for sequence tasks."""
    
    def __init__(self):
        self.model = None
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.training_history = {
            "loss_history": [],
            "val_loss_history": [],
            "accuracy_history": [],
            "val_accuracy_history": [],
            "epoch_times": [],
            "learning_rates": [],
        }
    
    def train(
        self,
        parameters: Dict[str, Any],
        config: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Train a Transformer model.
        
        Args:
            parameters: Training parameters including:
                - learning_rate: float, learning rate for optimizer
                - epochs: int, number of training epochs
                - batch_size: int, batch size for training
                - vocab_size: int, vocabulary size
                - d_model: int, model dimension
                - nhead: int, number of attention heads
                - num_encoder_layers: int, number of encoder layers
                - max_seq_length: int, maximum sequence length
                - num_classes: int, number of output classes
                - train_data: optional, training data as (sequences, labels) tuple
                - val_data: optional, validation data as (sequences, labels) tuple
            config: Additional configuration
            
        Returns:
            Dictionary with training results
        """
        config = config or {}
        
        try:
            # Extract parameters with defaults
            learning_rate = parameters.get("learning_rate", 0.0001)
            epochs = parameters.get("epochs", 5)
            batch_size = parameters.get("batch_size", 8)
            vocab_size = parameters.get("vocab_size", 1000)
            d_model = parameters.get("d_model", 512)
            nhead = parameters.get("nhead", 8)
            num_encoder_layers = parameters.get("num_encoder_layers", 6)
            max_seq_length = parameters.get("max_seq_length", 512)
            num_classes = parameters.get("num_classes", 10)
            dropout = parameters.get("dropout", 0.1)
            
            # Generate or use provided data
            train_data = parameters.get("train_data")
            val_data = parameters.get("val_data")
            
            if train_data is None:
                # Generate synthetic data for demonstration
                train_data = self._generate_synthetic_data(
                    n_samples=1000,
                    vocab_size=vocab_size,
                    max_seq_length=max_seq_length,
                    num_classes=num_classes,
                )
            
            if val_data is None:
                val_data = self._generate_synthetic_data(
                    n_samples=200,
                    vocab_size=vocab_size,
                    max_seq_length=max_seq_length,
                    num_classes=num_classes,
                )
            
            # Prepare data loaders
            train_loader = self._prepare_data_loader(train_data, batch_size, shuffle=True)
            val_loader = self._prepare_data_loader(val_data, batch_size, shuffle=False)
            
            # Initialize model
            self.model = SimpleTransformer(
                vocab_size=vocab_size,
                d_model=d_model,
                nhead=nhead,
                num_encoder_layers=num_encoder_layers,
                num_decoder_layers=0,  # Not using decoder
                max_seq_length=max_seq_length,
                num_classes=num_classes,
                dropout=dropout,
            ).to(self.device)
            
            # Loss function and optimizer
            criterion = nn.CrossEntropyLoss()
            optimizer = optim.AdamW(self.model.parameters(), lr=learning_rate)
            
            # Learning rate scheduler with warmup
            scheduler = self._create_scheduler(optimizer, epochs, config)
            
            # Training loop
            start_time = time.time()
            self.training_history = {
                "loss_history": [],
                "val_loss_history": [],
                "accuracy_history": [],
                "val_accuracy_history": [],
                "epoch_times": [],
                "learning_rates": [],
            }
            
            for epoch in range(epochs):
                epoch_start = time.time()
                
                # Training phase
                self.model.train()
                train_loss = 0.0
                train_correct = 0
                train_total = 0
                
                for sequences, labels in train_loader:
                    sequences, labels = sequences.to(self.device), labels.to(self.device)
                    
                    optimizer.zero_grad()
                    outputs = self.model(sequences)
                    loss = criterion(outputs, labels)
                    loss.backward()
                    
                    # Gradient clipping
                    torch.nn.utils.clip_grad_norm_(self.model.parameters(), 1.0)
                    
                    optimizer.step()
                    
                    train_loss += loss.item()
                    _, predicted = torch.max(outputs.data, 1)
                    train_total += labels.size(0)
                    train_correct += (predicted == labels).sum().item()
                
                avg_train_loss = train_loss / len(train_loader)
                train_accuracy = 100 * train_correct / train_total
                self.training_history["loss_history"].append(avg_train_loss)
                self.training_history["accuracy_history"].append(train_accuracy)
                
                # Validation phase
                val_loss, val_accuracy = self._evaluate_model(val_loader, criterion)
                self.training_history["val_loss_history"].append(val_loss)
                self.training_history["val_accuracy_history"].append(val_accuracy)
                
                # Update learning rate
                if scheduler:
                    scheduler.step()
                    current_lr = optimizer.param_groups[0]["lr"]
                    self.training_history["learning_rates"].append(current_lr)
                
                epoch_time = time.time() - epoch_start
                self.training_history["epoch_times"].append(epoch_time)
                
                # Log progress
                print(f"Epoch {epoch + 1}/{epochs} - "
                      f"Train Loss: {avg_train_loss:.4f}, Train Acc: {train_accuracy:.2f}% - "
                      f"Val Loss: {val_loss:.4f}, Val Acc: {val_accuracy:.2f}% - "
                      f"Time: {epoch_time:.2f}s")
            
            total_time = time.time() - start_time
            
            # Prepare results
            results = {
                "loss_history": self.training_history["loss_history"],
                "validation_loss": self.training_history["val_loss_history"],
                "accuracy_history": self.training_history["accuracy_history"],
                "validation_accuracy": self.training_history["val_accuracy_history"],
                "training_time": total_time,
                "learning_rates": self.training_history["learning_rates"],
                "model_summary": {
                    "vocab_size": vocab_size,
                    "d_model": d_model,
                    "nhead": nhead,
                    "num_encoder_layers": num_encoder_layers,
                    "max_seq_length": max_seq_length,
                    "num_classes": num_classes,
                    "parameters": sum(p.numel() for p in self.model.parameters()),
                    "trainable_parameters": sum(p.numel() for p in self.model.parameters() if p.requires_grad),
                },
                "final_accuracy": self.training_history["accuracy_history"][-1],
                "final_val_accuracy": self.training_history["val_accuracy_history"][-1],
                "device_used": str(self.device),
            }
            
            return results
            
        except Exception as e:
            raise TrainingError(f"Transformer training failed: {str(e)}") from e
    
    def validate(
        self,
        parameters: Dict[str, Any],
        config: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Validate the trained Transformer model."""
        if self.model is None:
            raise ValidationError("Model not trained. Call train() first.")
        
        config = config or {}
        
        try:
            # Extract validation data
            val_data = parameters.get("val_data")
            if val_data is None:
                # Get model configuration
                vocab_size = self.model.vocab_size
                max_seq_length = self.model.max_seq_length
                num_classes = self.model.fc_out.out_features
                
                val_data = self._generate_synthetic_data(
                    n_samples=200,
                    vocab_size=vocab_size,
                    max_seq_length=max_seq_length,
                    num_classes=num_classes,
                )
            
            # Prepare data loader
            batch_size = parameters.get("batch_size", 8)
            val_loader = self._prepare_data_loader(val_data, batch_size, shuffle=False)
            
            # Evaluate model
            criterion = nn.CrossEntropyLoss()
            val_loss, val_accuracy = self._evaluate_model(val_loader, criterion)
            
            # Calculate additional metrics
            self.model.eval()
            all_predictions = []
            all_labels = []
            all_attention_weights = []  # Would need to extract from model
            
            with torch.no_grad():
                for sequences, labels in val_loader:
                    sequences, labels = sequences.to(self.device), labels.to(self.device)
                    outputs = self.model(sequences)
                    
                    _, predictions = torch.max(outputs, 1)
                    
                    all_predictions.append(predictions.cpu().numpy())
                    all_labels.append(labels.cpu().numpy())
            
            predictions_np = np.concatenate(all_predictions)
            labels_np = np.concatenate(all_labels)
            
            # Calculate per-class metrics
            unique_classes = np.unique(np.concatenate([predictions_np, labels_np]))
            per_class_metrics = {}
            
            for cls in unique_classes:
                mask = labels_np == cls
                if np.sum(mask) > 0:
                    class_acc = np.mean(predictions_np[mask] == labels_np[mask])
                    per_class_metrics[int(cls)] = float(class_acc)
            
            return {
                "validation_loss": float(val_loss),
                "validation_accuracy": float(val_accuracy),
                "per_class_accuracy": per_class_metrics,
                "predictions": predictions_np.tolist(),
                "labels": labels_np.tolist(),
                "sample_count": len(predictions_np),
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
                    "vocab_size": self.model.vocab_size,
                    "d_model": self.model.d_model,
                    "nhead": self.model.transformer_encoder.layers[0].self_attn.num_heads,
                    "num_encoder_layers": len(self.model.transformer_encoder.layers),
                    "max_seq_length": self.model.max_seq_length,
                    "num_classes": self.model.fc_out.out_features,
                },
            }, path)
            return True
        except Exception as e:
            raise ModelSaveError(f"Failed to save model: {str(e)}") from e
    
    def load_model(self, path: str) -> bool:
        """Load a trained model from disk."""
        try:
            checkpoint = torch.load(path, map_location=self.device)
            
            model_config = checkpoint["model_config"]
            
            self.model = SimpleTransformer(
                vocab_size=model_config["vocab_size"],
                d_model=model_config["d_model"],
                nhead=model_config["nhead"],
                num_encoder_layers=model_config["num_encoder_layers"],
                num_decoder_layers=0,
                max_seq_length=model_config["max_seq_length"],
                num_classes=model_config["num_classes"],
            ).to(self.device)
            
            self.model.load_state_dict(checkpoint["model_state_dict"])
            self.training_history = checkpoint["training_history"]
            
            return True
        except Exception as e:
            raise ModelLoadError(f"Failed to load model: {str(e)}") from e
    
    # Helper methods
    def _generate_synthetic_data(
        self, 
        n_samples: int,
        vocab_size: int,
        max_seq_length: int,
        num_classes: int,
    ) -> tuple:
        """Generate synthetic sequence data."""
        # Generate random sequences
        seq_lengths = torch.randint(10, max_seq_length + 1, (n_samples,))
        sequences = []
        
        for length in seq_lengths:
            seq = torch.randint(1, vocab_size, (length,))  # 0 is usually padding
            # Pad to max_seq_length
            if length < max_seq_length:
                pad = torch.zeros(max_seq_length - length, dtype=torch.long)
                seq = torch.cat([seq, pad])
            else:
                seq = seq[:max_seq_length]
            sequences.append(seq)
        
        sequences = torch.stack(sequences)
        
        # Generate random labels
        labels = torch.randint(0, num_classes, (n_samples,))
        
        return sequences, labels
    
    def _prepare_data_loader(
        self, 
        data: tuple, 
        batch_size: int, 
        shuffle: bool
    ) -> DataLoader:
        """Prepare a PyTorch DataLoader from data tuple."""
        sequences, labels = data
        dataset = TensorDataset(sequences, labels)
        return DataLoader(dataset, batch_size=batch_size, shuffle=shuffle)
    
    def _evaluate_model(self, data_loader: DataLoader, criterion) -> tuple:
        """Evaluate model on data loader."""
        if self.model is None:
            return float("inf"), 0.0
        
        self.model.eval()
        total_loss = 0.0
        correct = 0
        total = 0
        
        with torch.no_grad():
            for sequences, labels in data_loader:
                sequences, labels = sequences.to(self.device), labels.to(self.device)
                outputs = self.model(sequences)
                loss = criterion(outputs, labels)
                
                total_loss += loss.item()
                _, predicted = torch.max(outputs.data, 1)
                total += labels.size(0)
                correct += (predicted == labels).sum().item()
        
        avg_loss = total_loss / len(data_loader)
        accuracy = 100 * correct / total
        
        return avg_loss, accuracy
    
    def _create_scheduler(self, optimizer, epochs: int, config: dict):
        """Create learning rate scheduler."""
        scheduler_type = config.get("scheduler", "cosine")
        
        if scheduler_type == "cosine":
            # Cosine annealing with warmup
            from torch.optim.lr_scheduler import CosineAnnealingWarmRestarts
            return CosineAnnealingWarmRestarts(
                optimizer,
                T_0=epochs // 4,
                T_mult=1,
                eta_min=1e-6,
            )
        elif scheduler_type == "step":
            # Step decay
            from torch.optim.lr_scheduler import StepLR
            return StepLR(optimizer, step_size=epochs // 3, gamma=0.1)
        else:
            # No scheduler
            return None