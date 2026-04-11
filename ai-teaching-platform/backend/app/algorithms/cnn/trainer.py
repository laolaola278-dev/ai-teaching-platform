"""
CNN trainer implementation for image classification.

This module provides a PyTorch-based CNN trainer following the
educational style of fastbook examples.
"""
import time
from typing import Any, Dict, Optional

import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
from torch.utils.data import DataLoader, TensorDataset
from torchvision import transforms

from app.algorithms.base.interface import BaseTrainer
from app.algorithms.base.exceptions import TrainingError, ValidationError


class SimpleCNN(nn.Module):
    """Simple CNN model for image classification."""
    
    def __init__(self, input_channels: int = 1, num_classes: int = 10):
        super().__init__()
        
        # Convolutional layers
        self.conv1 = nn.Conv2d(input_channels, 32, kernel_size=3, padding=1)
        self.conv2 = nn.Conv2d(32, 64, kernel_size=3, padding=1)
        self.conv3 = nn.Conv2d(64, 128, kernel_size=3, padding=1)
        
        # Pooling layer
        self.pool = nn.MaxPool2d(2, 2)
        
        # Fully connected layers
        # Assuming input images are 28x28 (MNIST-like)
        self.fc1 = nn.Linear(128 * 3 * 3, 256)  # After 3 pooling layers: 28 -> 14 -> 7 -> 3
        self.fc2 = nn.Linear(256, 128)
        self.fc3 = nn.Linear(128, num_classes)
        
        # Dropout for regularization
        self.dropout = nn.Dropout(0.5)
    
    def forward(self, x):
        # Convolutional layers with ReLU and pooling
        x = self.pool(F.relu(self.conv1(x)))
        x = self.pool(F.relu(self.conv2(x)))
        x = self.pool(F.relu(self.conv3(x)))
        
        # Flatten
        x = x.view(-1, 128 * 3 * 3)
        
        # Fully connected layers
        x = F.relu(self.fc1(x))
        x = self.dropout(x)
        x = F.relu(self.fc2(x))
        x = self.dropout(x)
        x = self.fc3(x)
        
        return x


class CNNTrainer(BaseTrainer):
    """CNN trainer for image classification tasks."""
    
    def __init__(self):
        self.model = None
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.training_history = {
            "loss_history": [],
            "val_loss_history": [],
            "accuracy_history": [],
            "val_accuracy_history": [],
            "epoch_times": [],
        }
    
    def train(
        self,
        parameters: Dict[str, Any],
        config: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Train a CNN model for image classification.
        
        Args:
            parameters: Training parameters including:
                - learning_rate: float, learning rate for optimizer
                - epochs: int, number of training epochs
                - batch_size: int, batch size for training
                - input_channels: int, number of input channels (1 for grayscale, 3 for RGB)
                - num_classes: int, number of output classes
                - image_size: tuple, input image size (height, width)
                - train_data: optional, training data as (images, labels) tuple
                - val_data: optional, validation data as (images, labels) tuple
            config: Additional configuration
            
        Returns:
            Dictionary with training results
        """
        config = config or {}
        
        try:
            # Extract parameters with defaults
            learning_rate = parameters.get("learning_rate", 0.001)
            epochs = parameters.get("epochs", 10)
            batch_size = parameters.get("batch_size", 32)
            input_channels = parameters.get("input_channels", 1)
            num_classes = parameters.get("num_classes", 10)
            image_size = parameters.get("image_size", (28, 28))
            
            # Generate or use provided data
            train_data = parameters.get("train_data")
            val_data = parameters.get("val_data")
            
            if train_data is None:
                # Generate synthetic data for demonstration
                train_data = self._generate_synthetic_data(
                    n_samples=1000,
                    input_channels=input_channels,
                    image_size=image_size,
                    num_classes=num_classes,
                )
            
            if val_data is None:
                val_data = self._generate_synthetic_data(
                    n_samples=200,
                    input_channels=input_channels,
                    image_size=image_size,
                    num_classes=num_classes,
                )
            
            # Prepare data loaders
            train_loader = self._prepare_data_loader(train_data, batch_size, shuffle=True)
            val_loader = self._prepare_data_loader(val_data, batch_size, shuffle=False)
            
            # Initialize model
            self.model = SimpleCNN(input_channels, num_classes).to(self.device)
            
            # Loss function and optimizer
            criterion = nn.CrossEntropyLoss()
            optimizer = optim.Adam(self.model.parameters(), lr=learning_rate)
            
            # Learning rate scheduler
            scheduler = optim.lr_scheduler.StepLR(optimizer, step_size=5, gamma=0.1)
            
            # Training loop
            start_time = time.time()
            self.training_history = {
                "loss_history": [],
                "val_loss_history": [],
                "accuracy_history": [],
                "val_accuracy_history": [],
                "epoch_times": [],
            }
            
            for epoch in range(epochs):
                epoch_start = time.time()
                
                # Training phase
                self.model.train()
                train_loss = 0.0
                train_correct = 0
                train_total = 0
                
                for images, labels in train_loader:
                    images, labels = images.to(self.device), labels.to(self.device)
                    
                    optimizer.zero_grad()
                    outputs = self.model(images)
                    loss = criterion(outputs, labels)
                    loss.backward()
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
                scheduler.step()
                
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
                "model_summary": {
                    "input_channels": input_channels,
                    "num_classes": num_classes,
                    "image_size": image_size,
                    "parameters": sum(p.numel() for p in self.model.parameters()),
                    "trainable_parameters": sum(p.numel() for p in self.model.parameters() if p.requires_grad),
                },
                "final_accuracy": self.training_history["accuracy_history"][-1],
                "final_val_accuracy": self.training_history["val_accuracy_history"][-1],
                "device_used": str(self.device),
            }
            
            return results
            
        except Exception as e:
            raise TrainingError(f"CNN training failed: {str(e)}") from e
    
    def validate(
        self,
        parameters: Dict[str, Any],
        config: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Validate the trained CNN model."""
        if self.model is None:
            raise ValidationError("Model not trained. Call train() first.")
        
        config = config or {}
        
        try:
            # Extract validation data
            val_data = parameters.get("val_data")
            if val_data is None:
                # Get model configuration
                input_channels = self.model.conv1.in_channels
                num_classes = self.model.fc3.out_features
                image_size = (28, 28)  # Default assumption
                
                val_data = self._generate_synthetic_data(
                    n_samples=200,
                    input_channels=input_channels,
                    image_size=image_size,
                    num_classes=num_classes,
                )
            
            # Prepare data loader
            batch_size = parameters.get("batch_size", 32)
            val_loader = self._prepare_data_loader(val_data, batch_size, shuffle=False)
            
            # Evaluate model
            criterion = nn.CrossEntropyLoss()
            val_loss, val_accuracy = self._evaluate_model(val_loader, criterion)
            
            # Calculate additional metrics
            self.model.eval()
            all_predictions = []
            all_labels = []
            all_probabilities = []
            
            with torch.no_grad():
                for images, labels in val_loader:
                    images, labels = images.to(self.device), labels.to(self.device)
                    outputs = self.model(images)
                    
                    probabilities = F.softmax(outputs, dim=1)
                    _, predictions = torch.max(outputs, 1)
                    
                    all_predictions.append(predictions.cpu().numpy())
                    all_labels.append(labels.cpu().numpy())
                    all_probabilities.append(probabilities.cpu().numpy())
            
            predictions_np = np.concatenate(all_predictions)
            labels_np = np.concatenate(all_labels)
            probabilities_np = np.concatenate(all_probabilities)
            
            # Calculate per-class accuracy
            class_accuracies = {}
            unique_classes = np.unique(labels_np)
            for cls in unique_classes:
                mask = labels_np == cls
                if np.sum(mask) > 0:
                    class_acc = np.mean(predictions_np[mask] == labels_np[mask])
                    class_accuracies[int(cls)] = float(class_acc)
            
            # Calculate confusion matrix (simplified)
            confusion = {}
            for true_cls in unique_classes:
                for pred_cls in unique_classes:
                    key = f"{true_cls}_{pred_cls}"
                    confusion[key] = int(np.sum((labels_np == true_cls) & (predictions_np == pred_cls)))
            
            return {
                "validation_loss": float(val_loss),
                "validation_accuracy": float(val_accuracy),
                "per_class_accuracy": class_accuracies,
                "confusion_matrix": confusion,
                "predictions": predictions_np.tolist(),
                "probabilities": probabilities_np.tolist(),
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
                    "input_channels": self.model.conv1.in_channels,
                    "num_classes": self.model.fc3.out_features,
                },
            }, path)
            return True
        except Exception as e:
            raise ModelSaveError(f"Failed to save model: {str(e)}") from e
    
    def load_model(self, path: str) -> bool:
        """Load a trained model from disk."""
        try:
            checkpoint = torch.load(path, map_location=self.device)
            
            input_channels = checkpoint["model_config"]["input_channels"]
            num_classes = checkpoint["model_config"]["num_classes"]
            
            self.model = SimpleCNN(input_channels, num_classes).to(self.device)
            self.model.load_state_dict(checkpoint["model_state_dict"])
            self.training_history = checkpoint["training_history"]
            
            return True
        except Exception as e:
            raise ModelLoadError(f"Failed to load model: {str(e)}") from e
    
    # Helper methods
    def _generate_synthetic_data(
        self, 
        n_samples: int,
        input_channels: int,
        image_size: tuple,
        num_classes: int,
    ) -> tuple:
        """Generate synthetic image data."""
        height, width = image_size
        
        # Generate random images
        images = torch.randn(n_samples, input_channels, height, width)
        
        # Generate random labels
        labels = torch.randint(0, num_classes, (n_samples,))
        
        return images, labels
    
    def _prepare_data_loader(
        self, 
        data: tuple, 
        batch_size: int, 
        shuffle: bool
    ) -> DataLoader:
        """Prepare a PyTorch DataLoader from data tuple."""
        images, labels = data
        dataset = TensorDataset(images, labels)
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
            for images, labels in data_loader:
                images, labels = images.to(self.device), labels.to(self.device)
                outputs = self.model(images)
                loss = criterion(outputs, labels)
                
                total_loss += loss.item()
                _, predicted = torch.max(outputs.data, 1)
                total += labels.size(0)
                correct += (predicted == labels).sum().item()
        
        avg_loss = total_loss / len(data_loader)
        accuracy = 100 * correct / total
        
        return avg_loss, accuracy