"""
Collaborative Filtering Model using Matrix Factorization
SVD-based recommendation system
"""

import numpy as np
import pandas as pd
from scipy.sparse import csr_matrix
from scipy.sparse.linalg import svds
import pickle
from pathlib import Path
from typing import List, Tuple, Dict

class CollaborativeFiltering:
    """
    Collaborative Filtering using Singular Value Decomposition (SVD)
    """
    
    def __init__(self, n_factors=50):
        """
        Args:
            n_factors: Number of latent factors
        """
        self.n_factors = n_factors
        self.user_factors = None
        self.item_factors = None
        self.user_id_map = {}
        self.item_id_map = {}
        self.reverse_user_map = {}
        self.reverse_item_map = {}
        self.global_mean = 0.0
        self.user_biases = {}
        self.item_biases = {}
        
    def _create_rating_matrix(self, df: pd.DataFrame) -> Tuple[np.ndarray, dict, dict]:
        """
        Create user-item rating matrix
        
        Args:
            df: DataFrame with columns [user_id, product_id, rating]
            
        Returns:
            rating_matrix, user_map, item_map
        """
        # Create mappings
        unique_users = sorted(df['user_id'].unique())
        unique_items = sorted(df['product_id'].unique())
        
        self.user_id_map = {user_id: idx for idx, user_id in enumerate(unique_users)}
        self.item_id_map = {item_id: idx for idx, item_id in enumerate(unique_items)}
        self.reverse_user_map = {idx: user_id for user_id, idx in self.user_id_map.items()}
        self.reverse_item_map = {idx: item_id for item_id, idx in self.item_id_map.items()}
        
        # Create rating matrix
        n_users = len(unique_users)
        n_items = len(unique_items)
        rating_matrix = np.zeros((n_users, n_items))
        
        for _, row in df.iterrows():
            user_idx = self.user_id_map[row['user_id']]
            item_idx = self.item_id_map[row['product_id']]
            rating_matrix[user_idx, item_idx] = row['rating']
        
        return rating_matrix, self.user_id_map, self.item_id_map
    
    def _normalize_ratings(self, rating_matrix: np.ndarray) -> np.ndarray:
        """
        Normalize ratings by subtracting user and item biases
        """
        # Global mean
        mask = rating_matrix > 0
        self.global_mean = rating_matrix[mask].mean()
        
        # User biases
        normalized = rating_matrix.copy()
        for user_idx in range(rating_matrix.shape[0]):
            user_ratings = rating_matrix[user_idx, rating_matrix[user_idx] > 0]
            if len(user_ratings) > 0:
                self.user_biases[user_idx] = user_ratings.mean() - self.global_mean
                normalized[user_idx, rating_matrix[user_idx] > 0] -= self.user_biases[user_idx]
        
        # Item biases
        for item_idx in range(rating_matrix.shape[1]):
            item_ratings = rating_matrix[:, item_idx]
            item_ratings = item_ratings[item_ratings > 0]
            if len(item_ratings) > 0:
                self.item_biases[item_idx] = item_ratings.mean() - self.global_mean
                normalized[rating_matrix[:, item_idx] > 0, item_idx] -= self.item_biases[item_idx]
        
        return normalized
    
    def train(self, ratings_df: pd.DataFrame, implicit_df: pd.DataFrame = None):
        """
        Train the CF model using SVD
        
        Args:
            ratings_df: DataFrame with explicit ratings (user_id, product_id, rating)
            implicit_df: Optional DataFrame with implicit feedback (user_id, product_id, interaction_type)
        """
        print(f"🤖 Training Collaborative Filtering Model...")
        print(f"   n_factors: {self.n_factors}")
        
        # Combine explicit and implicit feedback
        combined_df = ratings_df.copy()
        
        if implicit_df is not None:
            # Convert implicit feedback to ratings (binary or weighted)
            implicit_ratings = []
            for _, row in implicit_df.iterrows():
                # Weight different interaction types
                weights = {
                    'view': 0.5,
                    'click': 0.6,
                    'add_to_cart': 0.8,
                    'add_to_wishlist': 0.7,
                    'zoom': 0.4,
                    'purchase': 1.0
                }
                
                interaction_type = row.get('interaction_type', row.get('action', 'view'))
                weight = weights.get(interaction_type, 0.5)
                rating = 5.0 * weight  # Scale to 0-5
                
                implicit_ratings.append({
                    'user_id': row['user_id'],
                    'product_id': row['product_id'],
                    'rating': rating
                })
            
            implicit_df_processed = pd.DataFrame(implicit_ratings)
            combined_df = pd.concat([combined_df, implicit_df_processed], ignore_index=True)
            
            # Average ratings for same user-item pairs
            combined_df = combined_df.groupby(['user_id', 'product_id'])['rating'].mean().reset_index()
        
        print(f"   Total ratings: {len(combined_df)}")
        print(f"   Unique users: {combined_df['user_id'].nunique()}")
        print(f"   Unique items: {combined_df['product_id'].nunique()}")
        
        # Create rating matrix
        rating_matrix, _, _ = self._create_rating_matrix(combined_df)
        print(f"   Matrix shape: {rating_matrix.shape}")
        print(f"   Matrix sparsity: {(rating_matrix == 0).sum() / rating_matrix.size * 100:.2f}%")
        
        # Normalize ratings
        normalized_matrix = self._normalize_ratings(rating_matrix)
        
        # Perform SVD
        # Only decompose non-zero entries for efficiency with sparse data
        mask = rating_matrix > 0
        sparse_matrix = csr_matrix(normalized_matrix)
        
        k = min(self.n_factors, min(sparse_matrix.shape) - 1)
        print(f"   Computing SVD with k={k} factors...")
        
        U, sigma, Vt = svds(sparse_matrix, k=k)
        
        # Store factors
        self.user_factors = U
        self.item_factors = Vt.T
        self.sigma = np.diag(sigma)
        
        print(f"   ✅ Training completed!")
        print(f"   User factors shape: {self.user_factors.shape}")
        print(f"   Item factors shape: {self.item_factors.shape}")
    
    def predict(self, user_id: int, item_id: int) -> float:
        """
        Predict rating for user-item pair
        
        Returns:
            Predicted rating (0-5 scale)
        """
        if user_id not in self.user_id_map or item_id not in self.item_id_map:
            return self.global_mean
        
        user_idx = self.user_id_map[user_id]
        item_idx = self.item_id_map[item_id]
        
        # Base prediction from matrix factorization
        prediction = np.dot(
            np.dot(self.user_factors[user_idx], self.sigma),
            self.item_factors[item_idx]
        )
        
        # Add biases
        prediction += self.global_mean
        prediction += self.user_biases.get(user_idx, 0)
        prediction += self.item_biases.get(item_idx, 0)
        
        # Clip to valid range
        return np.clip(prediction, 0, 5)
    
    def recommend(self, user_id: int, k: int = 10, exclude_seen: bool = True) -> List[Tuple[int, float]]:
        """
        Recommend top-k items for a user
        
        Args:
            user_id: User ID
            k: Number of recommendations
            exclude_seen: Whether to exclude items user has already interacted with
            
        Returns:
            List of (item_id, predicted_rating) tuples
        """
        if user_id not in self.user_id_map:
            # Cold start: return popular items
            return self._recommend_popular(k)
        
        user_idx = self.user_id_map[user_id]
        
        # Predict ratings for all items
        user_vector = np.dot(self.user_factors[user_idx], self.sigma)
        predictions = np.dot(user_vector, self.item_factors.T)
        
        # Add biases
        predictions += self.global_mean
        predictions += self.user_biases.get(user_idx, 0)
        for item_idx in range(len(predictions)):
            predictions[item_idx] += self.item_biases.get(item_idx, 0)
        
        # Get top-k
        top_indices = np.argsort(predictions)[::-1]
        
        recommendations = []
        for idx in top_indices:
            item_id = self.reverse_item_map[idx]
            score = predictions[idx]
            recommendations.append((item_id, float(score)))
            
            if len(recommendations) >= k:
                break
        
        return recommendations
    
    def _recommend_popular(self, k: int = 10) -> List[Tuple[int, float]]:
        """Cold start: recommend popular items"""
        # Use item biases as popularity measure
        popular_items = sorted(
            self.item_biases.items(),
            key=lambda x: x[1],
            reverse=True
        )[:k]
        
        return [(self.reverse_item_map[idx], self.global_mean + bias) 
                for idx, bias in popular_items]
    
    def get_similar_users(self, user_id: int, k: int = 10) -> List[Tuple[int, float]]:
        """Find similar users based on latent factors"""
        if user_id not in self.user_id_map:
            return []
        
        user_idx = self.user_id_map[user_id]
        user_vector = self.user_factors[user_idx]
        
        # Compute cosine similarity
        similarities = np.dot(self.user_factors, user_vector)
        norms = np.linalg.norm(self.user_factors, axis=1) * np.linalg.norm(user_vector)
        similarities = similarities / (norms + 1e-8)
        
        # Get top-k (excluding self)
        top_indices = np.argsort(similarities)[::-1][1:k+1]
        
        return [(self.reverse_user_map[idx], float(similarities[idx])) 
                for idx in top_indices]
    
    def get_similar_items(self, item_id: int, k: int = 10) -> List[Tuple[int, float]]:
        """Find similar items based on latent factors"""
        if item_id not in self.item_id_map:
            return []
        
        item_idx = self.item_id_map[item_id]
        item_vector = self.item_factors[item_idx]
        
        # Compute cosine similarity
        similarities = np.dot(self.item_factors, item_vector)
        norms = np.linalg.norm(self.item_factors, axis=1) * np.linalg.norm(item_vector)
        similarities = similarities / (norms + 1e-8)
        
        # Get top-k (excluding self)
        top_indices = np.argsort(similarities)[::-1][1:k+1]
        
        return [(self.reverse_item_map[idx], float(similarities[idx])) 
                for idx in top_indices]
    
    def save(self, filepath: str):
        """Save model to disk"""
        model_data = {
            'n_factors': self.n_factors,
            'user_factors': self.user_factors,
            'item_factors': self.item_factors,
            'sigma': self.sigma,
            'user_id_map': self.user_id_map,
            'item_id_map': self.item_id_map,
            'reverse_user_map': self.reverse_user_map,
            'reverse_item_map': self.reverse_item_map,
            'global_mean': self.global_mean,
            'user_biases': self.user_biases,
            'item_biases': self.item_biases
        }
        
        with open(filepath, 'wb') as f:
            pickle.dump(model_data, f)
        
        print(f"💾 Model saved to: {filepath}")
    
    @classmethod
    def load(cls, filepath: str):
        """Load model from disk"""
        with open(filepath, 'rb') as f:
            model_data = pickle.load(f)
        
        model = cls(n_factors=model_data['n_factors'])
        model.user_factors = model_data['user_factors']
        model.item_factors = model_data['item_factors']
        model.sigma = model_data['sigma']
        model.user_id_map = model_data['user_id_map']
        model.item_id_map = model_data['item_id_map']
        model.reverse_user_map = model_data['reverse_user_map']
        model.reverse_item_map = model_data['reverse_item_map']
        model.global_mean = model_data['global_mean']
        model.user_biases = model_data['user_biases']
        model.item_biases = model_data['item_biases']
        
        print(f"📂 Model loaded from: {filepath}")
        return model
