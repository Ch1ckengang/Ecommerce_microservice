"""
Ensemble System - Kết hợp 3 mô hình ML
LSTM + Collaborative Filtering + Random Forest
"""

import numpy as np
import pickle
from typing import List, Tuple, Dict
from pathlib import Path

class EnsembleRecommender:
    """
    Ensemble of 3 models:
    1. LSTM (sequential patterns)
    2. Collaborative Filtering (user-item similarity)
    3. Random Forest (feature-based)
    """
    
    def __init__(self, method='weighted'):
        """
        Args:
            method: 'weighted' or 'stacking'
        """
        self.method = method
        self.lstm_model = None
        self.cf_model = None
        self.rf_model = None
        
        # Default weights (can be optimized)
        self.weights = {
            'lstm': 0.40,   # Sequential patterns
            'cf': 0.35,     # Collaborative filtering
            'rf': 0.25      # Feature-based
        }
        
        # For stacking
        self.meta_model = None
    
    def set_models(self, lstm_model, cf_model, rf_model):
        """Set the three base models"""
        self.lstm_model = lstm_model
        self.cf_model = cf_model
        self.rf_model = rf_model
        print("✅ Ensemble models set successfully")
    
    def set_weights(self, lstm_weight: float, cf_weight: float, rf_weight: float):
        """
        Set ensemble weights
        
        Args:
            lstm_weight: Weight for LSTM model
            cf_weight: Weight for CF model
            rf_weight: Weight for RF model
        """
        total = lstm_weight + cf_weight + rf_weight
        self.weights = {
            'lstm': lstm_weight / total,
            'cf': cf_weight / total,
            'rf': rf_weight / total
        }
        print(f"✅ Weights updated: LSTM={self.weights['lstm']:.2f}, "
              f"CF={self.weights['cf']:.2f}, RF={self.weights['rf']:.2f}")
    
    def predict_single(self, 
                      user_id: int,
                      product_id: int,
                      product_features: Dict = None) -> Dict[str, float]:
        """
        Get predictions from all models for a single user-product pair
        
        Args:
            user_id: User ID
            product_id: Product ID
            product_features: Product features dict
            
        Returns:
            Dict with predictions from each model and ensemble score
        """
        scores = {}
        
        # 1. LSTM prediction (if available)
        if self.lstm_model:
            try:
                # LSTM needs sequence, so this is simplified
                # In practice, you'd pass the user's action sequence
                lstm_score = 0.5  # Placeholder
                scores['lstm'] = lstm_score
            except Exception as e:
                print(f"LSTM prediction error: {e}")
                scores['lstm'] = 0.5
        else:
            scores['lstm'] = 0.5
        
        # 2. Collaborative Filtering prediction
        if self.cf_model:
            try:
                cf_score = self.cf_model.predict(user_id, product_id)
                # Normalize to 0-1
                scores['cf'] = cf_score / 5.0
            except Exception as e:
                print(f"CF prediction error: {e}")
                scores['cf'] = 0.5
        else:
            scores['cf'] = 0.5
        
        # 3. Random Forest prediction
        if self.rf_model and product_features:
            try:
                rf_score = self.rf_model.predict_proba(
                    user_id,
                    product_id,
                    product_features
                )
                scores['rf'] = rf_score
            except Exception as e:
                print(f"RF prediction error: {e}")
                scores['rf'] = 0.5
        else:
            scores['rf'] = 0.5
        
        # 4. Ensemble score
        if self.method == 'weighted':
            ensemble_score = (
                self.weights['lstm'] * scores['lstm'] +
                self.weights['cf'] * scores['cf'] +
                self.weights['rf'] * scores['rf']
            )
        else:
            # Stacking (not implemented yet)
            ensemble_score = np.mean([scores['lstm'], scores['cf'], scores['rf']])
        
        scores['ensemble'] = ensemble_score
        scores['confidence'] = self._calculate_confidence(scores)
        
        return scores
    
    def _calculate_confidence(self, scores: Dict[str, float]) -> float:
        """
        Calculate prediction confidence based on model agreement
        
        High confidence: all models agree
        Low confidence: models disagree
        """
        model_scores = [scores.get('lstm', 0.5), 
                       scores.get('cf', 0.5), 
                       scores.get('rf', 0.5)]
        
        # Use standard deviation as disagreement measure
        std = np.std(model_scores)
        
        # Convert to confidence (lower std = higher confidence)
        # Max std would be 0.5 (one model at 0, another at 1)
        confidence = 1.0 - (std / 0.5)
        return float(np.clip(confidence, 0, 1))
    
    def recommend(self,
                  user_id: int,
                  candidate_products: List[Dict],
                  k: int = 10,
                  diversity_weight: float = 0.0) -> List[Dict]:
        """
        Generate top-k recommendations using ensemble
        
        Args:
            user_id: User ID
            candidate_products: List of product dicts with features
            k: Number of recommendations
            diversity_weight: Weight for diversity (0-1)
            
        Returns:
            List of recommendation dicts with scores from all models
        """
        recommendations = []
        
        for product in candidate_products:
            product_id = product['product_id']
            
            # Get predictions from all models
            scores = self.predict_single(user_id, product_id, product)
            
            recommendation = {
                'product_id': product_id,
                'product': product,
                'score': scores['ensemble'],
                'model_scores': {
                    'lstm': scores['lstm'],
                    'cf': scores['cf'],
                    'rf': scores['rf']
                },
                'confidence': scores['confidence']
            }
            recommendations.append(recommendation)
        
        # Sort by ensemble score
        recommendations.sort(key=lambda x: x['score'], reverse=True)
        
        # Apply diversity if requested
        if diversity_weight > 0:
            recommendations = self._diversify(recommendations, diversity_weight)
        
        return recommendations[:k]
    
    def _diversify(self, 
                   recommendations: List[Dict],
                   diversity_weight: float) -> List[Dict]:
        """
        Re-rank recommendations to increase diversity
        Uses category diversity
        """
        if len(recommendations) == 0:
            return recommendations
        
        diversified = []
        seen_categories = set()
        
        # First pass: pick top items from different categories
        for rec in recommendations:
            category = rec['product'].get('category', 'Unknown')
            
            if category not in seen_categories:
                diversified.append(rec)
                seen_categories.add(category)
        
        # Second pass: fill remaining slots with top scores
        for rec in recommendations:
            if rec not in diversified:
                diversified.append(rec)
        
        return diversified
    
    def recommend_cf_only(self, user_id: int, k: int = 10) -> List[Tuple[int, float]]:
        """Recommend using CF model only"""
        if not self.cf_model:
            return []
        return self.cf_model.recommend(user_id, k)
    
    def recommend_rf_only(self, 
                          user_id: int,
                          candidate_products: List[Dict],
                          k: int = 10) -> List[Tuple[int, float]]:
        """Recommend using RF model only"""
        if not self.rf_model:
            return []
        return self.rf_model.recommend(user_id, candidate_products, k)
    
    def get_model_comparison(self, user_id: int, product_id: int, product_features: Dict) -> Dict:
        """
        Compare predictions from all models
        
        Returns:
            Dict with model comparisons and recommendation level
        """
        scores = self.predict_single(user_id, product_id, product_features)
        
        # Determine recommendation level
        ensemble_score = scores['ensemble']
        if ensemble_score >= 0.7:
            recommendation = "high"
        elif ensemble_score >= 0.5:
            recommendation = "medium"
        else:
            recommendation = "low"
        
        return {
            'user_id': user_id,
            'product_id': product_id,
            'lstm_score': scores['lstm'],
            'cf_score': scores['cf'],
            'rf_score': scores['rf'],
            'ensemble_score': scores['ensemble'],
            'confidence': scores['confidence'],
            'recommendation': recommendation,
            'model_agreement': {
                'high_agreement': scores['confidence'] >= 0.8,
                'models_agree': all(abs(scores[m] - ensemble_score) < 0.2 
                                  for m in ['lstm', 'cf', 'rf'])
            }
        }
    
    def optimize_weights(self, 
                        validation_data: List[Tuple[int, int, float]],
                        metric='mse'):
        """
        Optimize ensemble weights using validation data
        
        Args:
            validation_data: List of (user_id, product_id, actual_score) tuples
            metric: Optimization metric ('mse', 'mae', 'accuracy')
        """
        print(f"🔧 Optimizing ensemble weights using {metric}...")
        
        best_weights = self.weights.copy()
        best_score = float('inf') if metric in ['mse', 'mae'] else 0
        
        # Grid search over weight combinations
        for lstm_w in np.arange(0.2, 0.6, 0.05):
            for cf_w in np.arange(0.2, 0.6, 0.05):
                rf_w = 1.0 - lstm_w - cf_w
                if rf_w < 0.1 or rf_w > 0.6:
                    continue
                
                # Test this weight combination
                self.set_weights(lstm_w, cf_w, rf_w)
                
                # Compute metric on validation data
                errors = []
                for user_id, product_id, actual in validation_data[:100]:  # Sample
                    pred_scores = self.predict_single(user_id, product_id, {})
                    pred = pred_scores['ensemble']
                    
                    if metric == 'mse':
                        errors.append((pred - actual) ** 2)
                    elif metric == 'mae':
                        errors.append(abs(pred - actual))
                
                score = np.mean(errors) if errors else float('inf')
                
                if score < best_score:
                    best_score = score
                    best_weights = {'lstm': lstm_w, 'cf': cf_w, 'rf': rf_w}
        
        # Set best weights
        self.weights = best_weights
        print(f"   ✅ Best weights: LSTM={best_weights['lstm']:.3f}, "
              f"CF={best_weights['cf']:.3f}, RF={best_weights['rf']:.3f}")
        print(f"   📊 Best {metric}: {best_score:.4f}")
    
    def save(self, filepath: str):
        """Save ensemble configuration"""
        ensemble_data = {
            'method': self.method,
            'weights': self.weights
        }
        
        with open(filepath, 'wb') as f:
            pickle.dump(ensemble_data, f)
        
        print(f"💾 Ensemble config saved to: {filepath}")
    
    @classmethod
    def load(cls, filepath: str):
        """Load ensemble configuration"""
        with open(filepath, 'rb') as f:
            ensemble_data = pickle.load(f)
        
        ensemble = cls(method=ensemble_data['method'])
        ensemble.weights = ensemble_data['weights']
        
        print(f"📂 Ensemble config loaded from: {filepath}")
        return ensemble
