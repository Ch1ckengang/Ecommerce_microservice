"""
Hybrid Recommendation System
Combines LSTM, Knowledge Graph, and RAG recommendations
"""
import numpy as np
from typing import List, Dict, Tuple, Optional
import pickle
from collections import defaultdict

class HybridRecommender:
    """
    Hybrid recommendation system that combines:
    1. LSTM: Sequential behavior prediction
    2. Knowledge Graph: Relationship-based recommendations
    3. RAG: Semantic similarity search
    """
    
    def __init__(
        self,
        lstm_recommender=None,
        graph_recommender=None,
        rag_recommender=None,
        weights: Optional[Dict[str, float]] = None
    ):
        """
        Initialize hybrid recommender
        
        Args:
            lstm_recommender: LSTMRecommender instance
            graph_recommender: ProductKnowledgeGraph instance
            rag_recommender: ProductRAG instance
            weights: Dictionary with keys 'lstm', 'graph', 'rag'
        """
        self.lstm = lstm_recommender
        self.graph = graph_recommender
        self.rag = rag_recommender
        
        # Default weights
        self.weights = weights or {
            'lstm': 0.3,
            'graph': 0.3,
            'rag': 0.4
        }
        
        # Validate weights sum to 1.0
        total = sum(self.weights.values())
        if abs(total - 1.0) > 0.01:
            print(f"⚠️  Warning: Weights sum to {total}, normalizing...")
            for key in self.weights:
                self.weights[key] /= total
        
        print(f"✅ Hybrid Recommender initialized")
        print(f"   Weights: LSTM={self.weights['lstm']:.2f}, "
              f"Graph={self.weights['graph']:.2f}, "
              f"RAG={self.weights['rag']:.2f}")
    
    def normalize_scores(
        self,
        scores: List[Tuple[int, float]],
        method: str = 'minmax'
    ) -> Dict[int, float]:
        """
        Normalize scores to [0, 1] range
        
        Args:
            scores: List of (product_id, score) tuples
            method: Normalization method ('minmax' or 'zscore')
            
        Returns:
            Dictionary mapping product_id to normalized score
        """
        if not scores:
            return {}
        
        # Extract scores
        product_ids = [pid for pid, _ in scores]
        score_values = np.array([score for _, score in scores])
        
        if method == 'minmax':
            # Min-max normalization
            min_score = score_values.min()
            max_score = score_values.max()
            
            if max_score - min_score < 1e-6:
                # All scores are the same
                normalized = np.ones_like(score_values)
            else:
                normalized = (score_values - min_score) / (max_score - min_score)
        
        elif method == 'zscore':
            # Z-score normalization
            mean = score_values.mean()
            std = score_values.std()
            
            if std < 1e-6:
                normalized = np.ones_like(score_values)
            else:
                normalized = (score_values - mean) / std
                # Clip to [0, 1]
                normalized = np.clip(normalized, 0, 1)
        
        else:
            raise ValueError(f"Unknown normalization method: {method}")
        
        # Create dictionary
        return {pid: float(score) for pid, score in zip(product_ids, normalized)}
    
    def get_lstm_scores(
        self,
        user_sequence: List[int],
        k: int = 20,
        exclude_seen: bool = True
    ) -> Dict[int, float]:
        """
        Get LSTM recommendation scores
        
        Args:
            user_sequence: List of product IDs user has interacted with
            k: Number of recommendations
            exclude_seen: Exclude products in user_sequence
            
        Returns:
            Dictionary mapping product_id to normalized score
        """
        if self.lstm is None:
            print("⚠️  LSTM recommender not available")
            return {}
        
        try:
            # Get LSTM recommendations
            recommendations = self.lstm.recommend(
                product_ids=user_sequence,
                k=k,
                exclude_seen=exclude_seen
            )
            
            # Normalize scores
            normalized = self.normalize_scores(recommendations)
            
            return normalized
        
        except Exception as e:
            print(f"⚠️  LSTM error: {e}")
            return {}
    
    def get_graph_scores(
        self,
        user_id: Optional[int] = None,
        product_id: Optional[int] = None,
        k: int = 20
    ) -> Dict[int, float]:
        """
        Get Knowledge Graph recommendation scores
        
        Args:
            user_id: User ID for user-based recommendations
            product_id: Product ID for product-based recommendations
            k: Number of recommendations
            
        Returns:
            Dictionary mapping product_id to normalized score
        """
        if self.graph is None:
            print("⚠️  Graph recommender not available")
            return {}
        
        try:
            recommendations = []
            
            # User-based recommendations
            if user_id is not None:
                user_recs = self.graph.recommend_by_user_history(user_id, k=k)
                recommendations.extend(user_recs)
            
            # Product-based recommendations
            if product_id is not None:
                similar_recs = self.graph.recommend_similar_products(product_id, k=k)
                recommendations.extend(similar_recs)
                
                category_recs = self.graph.recommend_by_category(product_id, k=k)
                recommendations.extend(category_recs)
            
            # Aggregate scores for same products
            aggregated = defaultdict(float)
            for pid, score in recommendations:
                aggregated[pid] += score
            
            # Convert to list of tuples
            recommendations = list(aggregated.items())
            
            # Normalize scores
            normalized = self.normalize_scores(recommendations)
            
            return normalized
        
        except Exception as e:
            print(f"⚠️  Graph error: {e}")
            return {}
    
    def get_rag_scores(
        self,
        query: Optional[str] = None,
        product_id: Optional[int] = None,
        k: int = 20
    ) -> Dict[int, float]:
        """
        Get RAG recommendation scores
        
        Args:
            query: Text query for semantic search
            product_id: Product ID for similarity search
            k: Number of recommendations
            
        Returns:
            Dictionary mapping product_id to normalized score
        """
        if self.rag is None:
            print("⚠️  RAG recommender not available")
            return {}
        
        try:
            recommendations = []
            
            # Text-based search
            if query is not None:
                results = self.rag.search(query, k=k)
                recommendations = [(pid, score) for pid, score, _ in results]
            
            # Product-based similarity
            elif product_id is not None:
                recommendations = self.rag.recommend_by_product(product_id, k=k)
            
            # Normalize scores
            normalized = self.normalize_scores(recommendations)
            
            return normalized
        
        except Exception as e:
            print(f"⚠️  RAG error: {e}")
            return {}
    
    def combine_scores(
        self,
        lstm_scores: Dict[int, float],
        graph_scores: Dict[int, float],
        rag_scores: Dict[int, float]
    ) -> Dict[int, Dict[str, float]]:
        """
        Combine scores from all three sources
        
        Args:
            lstm_scores: LSTM scores
            graph_scores: Graph scores
            rag_scores: RAG scores
            
        Returns:
            Dictionary mapping product_id to score breakdown
        """
        # Get all unique product IDs
        all_products = set()
        all_products.update(lstm_scores.keys())
        all_products.update(graph_scores.keys())
        all_products.update(rag_scores.keys())
        
        # Combine scores
        combined = {}
        
        for pid in all_products:
            lstm_score = lstm_scores.get(pid, 0.0)
            graph_score = graph_scores.get(pid, 0.0)
            rag_score = rag_scores.get(pid, 0.0)
            
            # Weighted combination
            final_score = (
                self.weights['lstm'] * lstm_score +
                self.weights['graph'] * graph_score +
                self.weights['rag'] * rag_score
            )
            
            combined[pid] = {
                'final_score': final_score,
                'lstm': lstm_score,
                'graph': graph_score,
                'rag': rag_score
            }
        
        return combined
    
    def recommend(
        self,
        user_id: Optional[int] = None,
        user_sequence: Optional[List[int]] = None,
        query: Optional[str] = None,
        product_id: Optional[int] = None,
        k: int = 10,
        exclude_seen: bool = True
    ) -> List[Tuple[int, Dict[str, float]]]:
        """
        Get hybrid recommendations
        
        Args:
            user_id: User ID for graph-based recommendations
            user_sequence: User's product sequence for LSTM
            query: Text query for RAG search
            product_id: Product ID for similarity-based recommendations
            k: Number of recommendations to return
            exclude_seen: Exclude products in user_sequence
            
        Returns:
            List of (product_id, score_breakdown) tuples, sorted by final_score
        """
        print(f"\n🔮 Generating hybrid recommendations...")
        print(f"   User ID: {user_id}")
        print(f"   User sequence: {user_sequence}")
        print(f"   Query: {query}")
        print(f"   Product ID: {product_id}")
        print(f"   Top-K: {k}")
        
        # Get scores from each source
        lstm_scores = {}
        if user_sequence:
            print("\n📊 Getting LSTM scores...")
            lstm_scores = self.get_lstm_scores(user_sequence, k=k*2, exclude_seen=exclude_seen)
            print(f"   Found {len(lstm_scores)} products")
        
        graph_scores = {}
        if user_id or product_id:
            print("\n🕸️  Getting Graph scores...")
            graph_scores = self.get_graph_scores(user_id=user_id, product_id=product_id, k=k*2)
            print(f"   Found {len(graph_scores)} products")
        
        rag_scores = {}
        if query or product_id:
            print("\n🔍 Getting RAG scores...")
            rag_scores = self.get_rag_scores(query=query, product_id=product_id, k=k*2)
            print(f"   Found {len(rag_scores)} products")
        
        # Combine scores
        print("\n⚖️  Combining scores...")
        combined = self.combine_scores(lstm_scores, graph_scores, rag_scores)
        print(f"   Total unique products: {len(combined)}")
        
        # Sort by final score
        sorted_recommendations = sorted(
            combined.items(),
            key=lambda x: x[1]['final_score'],
            reverse=True
        )
        
        # Filter out seen products if requested
        if exclude_seen and user_sequence:
            seen_set = set(user_sequence)
            sorted_recommendations = [
                (pid, scores) for pid, scores in sorted_recommendations
                if pid not in seen_set
            ]
        
        # Return top-K
        top_k = sorted_recommendations[:k]
        
        print(f"\n✅ Returning top-{len(top_k)} recommendations")
        
        return top_k
    
    def explain_recommendation(
        self,
        product_id: int,
        score_breakdown: Dict[str, float]
    ) -> str:
        """
        Generate explanation for a recommendation
        
        Args:
            product_id: Product ID
            score_breakdown: Score breakdown from recommend()
            
        Returns:
            Explanation string
        """
        final_score = score_breakdown['final_score']
        lstm_score = score_breakdown['lstm']
        graph_score = score_breakdown['graph']
        rag_score = score_breakdown['rag']
        
        explanation = f"Sản phẩm {product_id} (Điểm: {final_score:.4f})\n"
        
        # Identify main contributor
        scores = {
            'LSTM (Hành vi tuần tự)': lstm_score,
            'Graph (Mối quan hệ)': graph_score,
            'RAG (Tương đồng ngữ nghĩa)': rag_score
        }
        
        main_source = max(scores.items(), key=lambda x: x[1])
        
        explanation += f"  Nguồn chính: {main_source[0]} ({main_source[1]:.4f})\n"
        explanation += f"  Chi tiết:\n"
        explanation += f"    - LSTM: {lstm_score:.4f} (trọng số {self.weights['lstm']:.2f})\n"
        explanation += f"    - Graph: {graph_score:.4f} (trọng số {self.weights['graph']:.2f})\n"
        explanation += f"    - RAG: {rag_score:.4f} (trọng số {self.weights['rag']:.2f})\n"
        
        return explanation
    
    def set_weights(self, lstm: float, graph: float, rag: float):
        """
        Update recommendation weights
        
        Args:
            lstm: LSTM weight
            graph: Graph weight
            rag: RAG weight
        """
        total = lstm + graph + rag
        
        self.weights = {
            'lstm': lstm / total,
            'graph': graph / total,
            'rag': rag / total
        }
        
        print(f"✅ Updated weights:")
        print(f"   LSTM: {self.weights['lstm']:.2f}")
        print(f"   Graph: {self.weights['graph']:.2f}")
        print(f"   RAG: {self.weights['rag']:.2f}")
    
    def save_config(self, path: str = 'data/hybrid_config.pkl'):
        """Save hybrid recommender configuration"""
        config = {
            'weights': self.weights
        }
        
        with open(path, 'wb') as f:
            pickle.dump(config, f)
        
        print(f"💾 Saved hybrid config to {path}")
    
    def load_config(self, path: str = 'data/hybrid_config.pkl'):
        """Load hybrid recommender configuration"""
        with open(path, 'rb') as f:
            config = pickle.load(f)
        
        self.weights = config['weights']
        
        print(f"✅ Loaded hybrid config from {path}")
        print(f"   Weights: {self.weights}")


if __name__ == '__main__':
    # Test hybrid recommender
    print("=" * 70)
    print("Testing Hybrid Recommender")
    print("=" * 70)
    
    # This is a placeholder test
    # In run_phase5.py, we'll load actual models
    
    hybrid = HybridRecommender(
        weights={'lstm': 0.3, 'graph': 0.3, 'rag': 0.4}
    )
    
    # Test score normalization
    print("\n" + "=" * 70)
    print("Test: Score Normalization")
    print("=" * 70)
    
    test_scores = [(1, 0.8), (2, 0.6), (3, 0.9), (4, 0.3), (5, 0.7)]
    normalized = hybrid.normalize_scores(test_scores)
    
    print("\nOriginal scores:")
    for pid, score in test_scores:
        print(f"  Product {pid}: {score:.4f}")
    
    print("\nNormalized scores:")
    for pid, score in normalized.items():
        print(f"  Product {pid}: {score:.4f}")
    
    # Test score combination
    print("\n" + "=" * 70)
    print("Test: Score Combination")
    print("=" * 70)
    
    lstm_scores = {1: 0.8, 2: 0.6, 3: 0.4}
    graph_scores = {2: 0.7, 3: 0.9, 4: 0.5}
    rag_scores = {1: 0.5, 3: 0.8, 4: 0.6, 5: 0.7}
    
    combined = hybrid.combine_scores(lstm_scores, graph_scores, rag_scores)
    
    print("\nCombined scores:")
    for pid in sorted(combined.keys()):
        scores = combined[pid]
        print(f"\nProduct {pid}:")
        print(f"  Final: {scores['final_score']:.4f}")
        print(f"  LSTM: {scores['lstm']:.4f}")
        print(f"  Graph: {scores['graph']:.4f}")
        print(f"  RAG: {scores['rag']:.4f}")
    
    print("\n✅ Hybrid recommender test complete!")
