"""
Training script for LSTM recommendation model
"""
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
import numpy as np
from sklearn.model_selection import train_test_split
from typing import Tuple
import time

from lstm_model import LSTMRecommender

class ProductSequenceDataset(Dataset):
    """PyTorch Dataset for product sequences"""
    
    def __init__(self, X: np.ndarray, y: np.ndarray):
        """
        Initialize dataset
        
        Args:
            X: Input sequences [N, seq_length]
            y: Target products [N]
        """
        self.X = torch.LongTensor(X)
        self.y = torch.LongTensor(y)
    
    def __len__(self):
        return len(self.X)
    
    def __getitem__(self, idx):
        return self.X[idx], self.y[idx]


class LSTMTrainer:
    """Trainer for LSTM recommendation model"""
    
    def __init__(
        self,
        recommender: LSTMRecommender,
        learning_rate: float = 0.001,
        weight_decay: float = 1e-5
    ):
        """
        Initialize trainer
        
        Args:
            recommender: LSTMRecommender instance
            learning_rate: Learning rate for optimizer
            weight_decay: L2 regularization
        """
        self.recommender = recommender
        self.model = recommender.model
        self.device = recommender.device
        
        # Loss function: CrossEntropyLoss
        self.criterion = nn.CrossEntropyLoss(ignore_index=0)  # Ignore padding
        
        # Optimizer: Adam
        self.optimizer = optim.Adam(
            self.model.parameters(),
            lr=learning_rate,
            weight_decay=weight_decay
        )
        
        # Learning rate scheduler
        self.scheduler = optim.lr_scheduler.ReduceLROnPlateau(
            self.optimizer,
            mode='min',
            factor=0.5,
            patience=3
        )
        
        # Training history
        self.history = {
            'train_loss': [],
            'val_loss': [],
            'train_acc': [],
            'val_acc': []
        }
    
    def train_epoch(self, train_loader: DataLoader) -> Tuple[float, float]:
        """
        Train for one epoch
        
        Args:
            train_loader: Training data loader
            
        Returns:
            Average loss and accuracy
        """
        self.model.train()
        
        total_loss = 0
        correct = 0
        total = 0
        
        for batch_idx, (sequences, targets) in enumerate(train_loader):
            # Move to device
            sequences = sequences.to(self.device)
            targets = targets.to(self.device)
            
            # Forward pass
            outputs = self.model(sequences)
            loss = self.criterion(outputs, targets)
            
            # Backward pass
            self.optimizer.zero_grad()
            loss.backward()
            
            # Gradient clipping
            torch.nn.utils.clip_grad_norm_(self.model.parameters(), max_norm=5.0)
            
            # Update weights
            self.optimizer.step()
            
            # Statistics
            total_loss += loss.item()
            _, predicted = outputs.max(1)
            total += targets.size(0)
            correct += predicted.eq(targets).sum().item()
            
            # Print progress
            if (batch_idx + 1) % 10 == 0:
                print(f'   Batch [{batch_idx + 1}/{len(train_loader)}] '
                      f'Loss: {loss.item():.4f} '
                      f'Acc: {100. * correct / total:.2f}%')
        
        avg_loss = total_loss / len(train_loader)
        accuracy = 100. * correct / total
        
        return avg_loss, accuracy
    
    def validate(self, val_loader: DataLoader) -> Tuple[float, float]:
        """
        Validate model
        
        Args:
            val_loader: Validation data loader
            
        Returns:
            Average loss and accuracy
        """
        self.model.eval()
        
        total_loss = 0
        correct = 0
        total = 0
        
        with torch.no_grad():
            for sequences, targets in val_loader:
                # Move to device
                sequences = sequences.to(self.device)
                targets = targets.to(self.device)
                
                # Forward pass
                outputs = self.model(sequences)
                loss = self.criterion(outputs, targets)
                
                # Statistics
                total_loss += loss.item()
                _, predicted = outputs.max(1)
                total += targets.size(0)
                correct += predicted.eq(targets).sum().item()
        
        avg_loss = total_loss / len(val_loader)
        accuracy = 100. * correct / total
        
        return avg_loss, accuracy
    
    def train(
        self,
        train_loader: DataLoader,
        val_loader: DataLoader,
        num_epochs: int = 20,
        early_stopping_patience: int = 5
    ):
        """
        Train model
        
        Args:
            train_loader: Training data loader
            val_loader: Validation data loader
            num_epochs: Number of epochs
            early_stopping_patience: Patience for early stopping
        """
        print("=" * 70)
        print("🚀 Starting Training")
        print("=" * 70)
        print(f"Device: {self.device}")
        print(f"Epochs: {num_epochs}")
        print(f"Train batches: {len(train_loader)}")
        print(f"Val batches: {len(val_loader)}")
        print("=" * 70)
        
        best_val_loss = float('inf')
        patience_counter = 0
        
        for epoch in range(num_epochs):
            start_time = time.time()
            
            print(f"\n📊 Epoch {epoch + 1}/{num_epochs}")
            print("-" * 70)
            
            # Train
            train_loss, train_acc = self.train_epoch(train_loader)
            
            # Validate
            val_loss, val_acc = self.validate(val_loader)
            
            # Update scheduler
            self.scheduler.step(val_loss)
            
            # Save history
            self.history['train_loss'].append(train_loss)
            self.history['val_loss'].append(val_loss)
            self.history['train_acc'].append(train_acc)
            self.history['val_acc'].append(val_acc)
            
            # Print epoch summary
            epoch_time = time.time() - start_time
            print("-" * 70)
            print(f"Epoch {epoch + 1} Summary:")
            print(f"   Train Loss: {train_loss:.4f} | Train Acc: {train_acc:.2f}%")
            print(f"   Val Loss:   {val_loss:.4f} | Val Acc:   {val_acc:.2f}%")
            print(f"   Time: {epoch_time:.2f}s")
            
            # Early stopping
            if val_loss < best_val_loss:
                best_val_loss = val_loss
                patience_counter = 0
                print(f"   ✅ New best validation loss!")
                
                # Save best model
                self.recommender.save_model(
                    'models/lstm_model_best.pth',
                    config={
                        'embedding_dim': self.model.embedding_dim,
                        'hidden_dim': self.model.hidden_dim,
                        'num_layers': self.model.num_layers,
                        'vocab_size': self.model.vocab_size
                    }
                )
            else:
                patience_counter += 1
                print(f"   Patience: {patience_counter}/{early_stopping_patience}")
                
                if patience_counter >= early_stopping_patience:
                    print(f"\n⚠️  Early stopping triggered!")
                    break
        
        print("\n" + "=" * 70)
        print("✅ Training Complete!")
        print("=" * 70)
        print(f"Best Val Loss: {best_val_loss:.4f}")
        print(f"Final Train Acc: {self.history['train_acc'][-1]:.2f}%")
        print(f"Final Val Acc: {self.history['val_acc'][-1]:.2f}%")


def train_lstm_model(
    X_path: str = 'data/X_train.npy',
    y_path: str = 'data/y_train.npy',
    mappings_path: str = 'data/mappings.pkl',
    batch_size: int = 32,
    num_epochs: int = 20,
    learning_rate: float = 0.001,
    val_split: float = 0.2,
    random_state: int = 42
):
    """
    Complete training pipeline
    
    Args:
        X_path: Path to input sequences
        y_path: Path to target products
        mappings_path: Path to product mappings
        batch_size: Batch size
        num_epochs: Number of epochs
        learning_rate: Learning rate
        val_split: Validation split ratio
        random_state: Random seed
    """
    print("=" * 70)
    print("📌 PHASE 2 — LSTM MODEL TRAINING")
    print("=" * 70)
    
    # Set random seed
    torch.manual_seed(random_state)
    np.random.seed(random_state)
    
    # Load data
    print("\n📂 Loading data...")
    X = np.load(X_path)
    y = np.load(y_path)
    print(f"   X shape: {X.shape}")
    print(f"   y shape: {y.shape}")
    
    # Split data
    print(f"\n✂️  Splitting data (val_split={val_split})...")
    X_train, X_val, y_train, y_val = train_test_split(
        X, y, test_size=val_split, random_state=random_state
    )
    print(f"   Train: {len(X_train)} samples")
    print(f"   Val:   {len(X_val)} samples")
    
    # Create datasets
    train_dataset = ProductSequenceDataset(X_train, y_train)
    val_dataset = ProductSequenceDataset(X_val, y_val)
    
    # Create data loaders
    train_loader = DataLoader(
        train_dataset,
        batch_size=batch_size,
        shuffle=True,
        num_workers=0
    )
    val_loader = DataLoader(
        val_dataset,
        batch_size=batch_size,
        shuffle=False,
        num_workers=0
    )
    
    # Create model
    print("\n🏗️  Creating model...")
    recommender = LSTMRecommender(mappings_path=mappings_path)
    recommender.create_model(
        embedding_dim=64,
        hidden_dim=128,
        num_layers=2,
        dropout=0.3
    )
    
    # Create trainer
    trainer = LSTMTrainer(
        recommender=recommender,
        learning_rate=learning_rate
    )
    
    # Train
    trainer.train(
        train_loader=train_loader,
        val_loader=val_loader,
        num_epochs=num_epochs,
        early_stopping_patience=5
    )
    
    # Save final model
    print("\n💾 Saving final model...")
    recommender.save_model(
        'models/lstm_model.pth',
        config={
            'embedding_dim': 64,
            'hidden_dim': 128,
            'num_layers': 2,
            'vocab_size': recommender.num_products
        }
    )
    
    return recommender, trainer


if __name__ == '__main__':
    # Train model
    recommender, trainer = train_lstm_model(
        batch_size=32,
        num_epochs=20,
        learning_rate=0.001
    )
