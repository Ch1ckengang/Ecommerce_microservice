"""
LSTM Model for Product Recommendation
Uses PyTorch to predict next product based on user behavior sequence
"""
import torch
import torch.nn as nn
import numpy as np
from typing import List, Tuple
import pickle

class ProductRecommenderLSTM(nn.Module):
    """
    LSTM-based product recommendation model
    
    Architecture:
    - Embedding layer: Convert product indices to dense vectors
    - LSTM layer: Process sequential behavior
    - Linear layer: Predict next product
    """
    
    def __init__(
        self, 
        vocab_size: int,
        embedding_dim: int = 64,
        hidden_dim: int = 128,
        num_layers: int = 2,
        dropout: float = 0.3
    ):
        """
        Initialize LSTM model
        
        Args:
            vocab_size: Number of unique products (including padding)
            embedding_dim: Dimension of product embeddings
            hidden_dim: LSTM hidden state dimension
            num_layers: Number of LSTM layers
            dropout: Dropout rate for regularization
        """
        super(ProductRecommenderLSTM, self).__init__()
        
        self.vocab_size = vocab_size
        self.embedding_dim = embedding_dim
        self.hidden_dim = hidden_dim
        self.num_layers = num_layers
        
        # Embedding layer: product_id -> dense vector
        self.embedding = nn.Embedding(
            num_embeddings=vocab_size,
            embedding_dim=embedding_dim,
            padding_idx=0  # Index 0 is padding
        )
        
        # LSTM layer: process sequence
        self.lstm = nn.LSTM(
            input_size=embedding_dim,
            hidden_size=hidden_dim,
            num_layers=num_layers,
            batch_first=True,
            dropout=dropout if num_layers > 1 else 0
        )
        
        # Dropout for regularization
        self.dropout = nn.Dropout(dropout)
        
        # Output layer: hidden state -> product scores
        self.fc = nn.Linear(hidden_dim, vocab_size)
        
        # Initialize weights
        self._init_weights()
    
    def _init_weights(self):
        """Initialize model weights"""
        # Initialize embedding
        nn.init.uniform_(self.embedding.weight, -0.1, 0.1)
        self.embedding.weight.data[0] = 0  # Padding embedding = 0
        
        # Initialize LSTM
        for name, param in self.lstm.named_parameters():
            if 'weight' in name:
                nn.init.xavier_uniform_(param)
            elif 'bias' in name:
                nn.init.zeros_(param)
        
        # Initialize linear layer
        nn.init.xavier_uniform_(self.fc.weight)
        nn.init.zeros_(self.fc.bias)
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Forward pass
        
        Args:
            x: Input sequences [batch_size, seq_length]
            
        Returns:
            logits: Product scores [batch_size, vocab_size]
        """
        # Embedding: [batch_size, seq_length] -> [batch_size, seq_length, embedding_dim]
        embedded = self.embedding(x)
        
        # LSTM: [batch_size, seq_length, embedding_dim] -> [batch_size, seq_length, hidden_dim]
        lstm_out, (hidden, cell) = self.lstm(embedded)
        
        # Take last hidden state: [batch_size, hidden_dim]
        last_hidden = lstm_out[:, -1, :]
        
        # Apply dropout
        last_hidden = self.dropout(last_hidden)
        
        # Linear: [batch_size, hidden_dim] -> [batch_size, vocab_size]
        logits = self.fc(last_hidden)
        
        return logits
    
    def predict_top_k(
        self, 
        sequence: List[int], 
        k: int = 10,
        exclude_seen: bool = True
    ) -> List[Tuple[int, float]]:
        """
        Predict top-K products for a given sequence
        
        Args:
            sequence: List of product indices
            k: Number of recommendations
            exclude_seen: Whether to exclude products already in sequence
            
        Returns:
            List of (product_idx, score) tuples
        """
        self.eval()
        
        with torch.no_grad():
            # Convert to tensor
            x = torch.LongTensor([sequence])
            
            # Forward pass
            logits = self.forward(x)
            
            # Apply softmax to get probabilities
            probs = torch.softmax(logits, dim=1)
            
            # Get scores
            scores = probs[0].cpu().numpy()
            
            # Exclude padding (index 0)
            scores[0] = -1
            
            # Exclude seen products if requested
            if exclude_seen:
                for idx in sequence:
                    if 0 < idx < len(scores):
                        scores[idx] = -1
            
            # Get top-K indices
            top_k_indices = np.argsort(scores)[-k:][::-1]
            
            # Create result list
            recommendations = [
                (int(idx), float(scores[idx])) 
                for idx in top_k_indices
                if scores[idx] > 0
            ]
            
            return recommendations[:k]
    
    def get_embedding(self, product_idx: int) -> np.ndarray:
        """
        Get embedding vector for a product
        
        Args:
            product_idx: Product index
            
        Returns:
            Embedding vector
        """
        self.eval()
        
        with torch.no_grad():
            embedding = self.embedding.weight[product_idx].cpu().numpy()
        
        return embedding


class LSTMRecommender:
    """
    Wrapper class for LSTM model with utilities
    """
    
    def __init__(
        self,
        model_path: str = None,
        mappings_path: str = 'data/mappings.pkl'
    ):
        """
        Initialize recommender
        
        Args:
            model_path: Path to saved model
            mappings_path: Path to product mappings
        """
        self.model = None
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.product_to_idx = {}
        self.idx_to_product = {}
        self.num_products = 0
        
        # Load mappings
        self.load_mappings(mappings_path)
        
        # Load model if path provided
        if model_path:
            self.load_model(model_path)
    
    def load_mappings(self, mappings_path: str):
        """Load product ID mappings"""
        with open(mappings_path, 'rb') as f:
            mappings = pickle.load(f)
        
        self.product_to_idx = mappings['product_to_idx']
        self.idx_to_product = mappings['idx_to_product']
        self.num_products = mappings['num_products']
        
        print(f"✅ Loaded mappings: {self.num_products} products")
    
    def create_model(
        self,
        embedding_dim: int = 64,
        hidden_dim: int = 128,
        num_layers: int = 2,
        dropout: float = 0.3
    ):
        """Create new model"""
        self.model = ProductRecommenderLSTM(
            vocab_size=self.num_products,
            embedding_dim=embedding_dim,
            hidden_dim=hidden_dim,
            num_layers=num_layers,
            dropout=dropout
        ).to(self.device)
        
        print(f"✅ Created model on {self.device}")
        print(f"   Parameters: {sum(p.numel() for p in self.model.parameters()):,}")
    
    def load_model(self, model_path: str):
        """Load trained model"""
        checkpoint = torch.load(model_path, map_location=self.device)
        
        # Create model with saved config
        config = checkpoint.get('config', {})
        self.create_model(
            embedding_dim=config.get('embedding_dim', 64),
            hidden_dim=config.get('hidden_dim', 128),
            num_layers=config.get('num_layers', 2),
            dropout=config.get('dropout', 0.3)
        )
        
        # Load weights
        self.model.load_state_dict(checkpoint['model_state_dict'])
        self.model.eval()
        
        print(f"✅ Loaded model from {model_path}")
    
    def save_model(self, model_path: str, config: dict = None):
        """Save model"""
        checkpoint = {
            'model_state_dict': self.model.state_dict(),
            'config': config or {
                'embedding_dim': self.model.embedding_dim,
                'hidden_dim': self.model.hidden_dim,
                'num_layers': self.model.num_layers,
                'vocab_size': self.model.vocab_size
            }
        }
        
        torch.save(checkpoint, model_path)
        print(f"✅ Saved model to {model_path}")
    
    def recommend(
        self,
        product_ids: List[int],
        k: int = 10,
        exclude_seen: bool = True
    ) -> List[Tuple[int, float]]:
        """
        Get recommendations for a sequence of product IDs
        
        Args:
            product_ids: List of product IDs (not indices)
            k: Number of recommendations
            exclude_seen: Exclude products already seen
            
        Returns:
            List of (product_id, score) tuples
        """
        if not self.model:
            raise ValueError("Model not loaded. Call create_model() or load_model() first.")
        
        # Convert product IDs to indices
        sequence = [
            self.product_to_idx.get(pid, 0) 
            for pid in product_ids
        ]
        
        # Get predictions
        predictions = self.model.predict_top_k(sequence, k=k, exclude_seen=exclude_seen)
        
        # Convert indices back to product IDs
        recommendations = [
            (self.idx_to_product.get(idx, 0), score)
            for idx, score in predictions
        ]
        
        return recommendations


if __name__ == '__main__':
    # Test model creation
    print("Testing LSTM Model...")
    
    recommender = LSTMRecommender(mappings_path='data/mappings.pkl')
    recommender.create_model(
        embedding_dim=64,
        hidden_dim=128,
        num_layers=2,
        dropout=0.3
    )
    
    print("\n✅ Model architecture:")
    print(recommender.model)
    
    # Test forward pass
    batch_size = 4
    seq_length = 20
    x = torch.randint(0, recommender.num_products, (batch_size, seq_length))
    
    output = recommender.model(x)
    print(f"\n✅ Forward pass test:")
    print(f"   Input shape: {x.shape}")
    print(f"   Output shape: {output.shape}")
    
    # Test prediction
    test_sequence = [1, 2, 3, 4, 5]
    recommendations = recommender.recommend(test_sequence, k=5)
    print(f"\n✅ Prediction test:")
    print(f"   Input: {test_sequence}")
    print(f"   Top-5 recommendations: {recommendations}")
