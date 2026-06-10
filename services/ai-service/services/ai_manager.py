"""
AI Manager - Manages all AI models and provides unified interface
"""
import sys
import os
from typing import Optional, List, Dict, Tuple

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from lstm_model import LSTMRecommender
from graph import ProductKnowledgeGraph
from rag import ProductRAG, ProductChatbot
from hybrid import HybridRecommender
from services.service_manager import ServiceManager

class AIManager:
    """
    Manages all AI components:
    - LSTM Recommender
    - Knowledge Graph
    - RAG System
    - Hybrid Recommender
    """
    
    def __init__(self):
        """Initialize AI Manager"""
        self.lstm: Optional[LSTMRecommender] = None
        self.graph: Optional[ProductKnowledgeGraph] = None
        self.rag: Optional[ProductRAG] = None
        self.chatbot: Optional[ProductChatbot] = None
        self.hybrid: Optional[HybridRecommender] = None
        self.service_manager: Optional[ServiceManager] = None
        
        self.initialized = False
        self.component_status = {
            'lstm': 'not_loaded',
            'graph': 'not_loaded',
            'rag': 'not_loaded',
            'hybrid': 'not_loaded',
            'services': 'not_loaded'
        }
    
    async def initialize(self):
        """
        Initialize all AI components
        """
        if self.initialized:
            print("⚠️  AI Manager already initialized")
            return
        
        print("🔄 Initializing AI Manager...")
        
        # Load LSTM
        try:
            print("📊 Loading LSTM Recommender...")
            self.lstm = LSTMRecommender(
                model_path='models/lstm_model_best.pth',
                mappings_path='data/mappings.pkl'
            )
            self.component_status['lstm'] = 'healthy'
            print("✅ LSTM loaded")
        except Exception as e:
            print(f"⚠️  LSTM load failed: {e}")
            self.component_status['lstm'] = 'error'
            self.lstm = None
        
        # Load Knowledge Graph
        try:
            print("🕸️  Connecting to Knowledge Graph...")
            self.graph = ProductKnowledgeGraph(
                uri="bolt://localhost:7687",
                user="neo4j",
                password="password123"
            )
            self.component_status['graph'] = 'healthy'
            print("✅ Graph connected")
        except Exception as e:
            print(f"⚠️  Graph connection failed: {e}")
            self.component_status['graph'] = 'error'
            self.graph = None
        
        # Load RAG
        try:
            print("🔍 Loading RAG System...")
            self.rag = ProductRAG()
            self.rag.load(
                index_path='data/faiss_index.bin',
                metadata_path='data/rag_metadata.pkl'
            )
            
            # Initialize chatbot
            self.chatbot = ProductChatbot(self.rag)
            
            self.component_status['rag'] = 'healthy'
            print("✅ RAG loaded")
        except Exception as e:
            print(f"⚠️  RAG load failed: {e}")
            self.component_status['rag'] = 'error'
            self.rag = None
            self.chatbot = None
        
        # Initialize Hybrid Recommender
        try:
            print("⚖️  Initializing Hybrid Recommender...")
            self.hybrid = HybridRecommender(
                lstm_recommender=self.lstm,
                graph_recommender=self.graph,
                rag_recommender=self.rag,
                weights={'lstm': 0.3, 'graph': 0.3, 'rag': 0.4}
            )
            self.component_status['hybrid'] = 'healthy'
            print("✅ Hybrid initialized")
        except Exception as e:
            print(f"⚠️  Hybrid initialization failed: {e}")
            self.component_status['hybrid'] = 'error'
            self.hybrid = None
        
        # Initialize Service Manager
        try:
            print("🔗 Initializing Service Manager...")
            self.service_manager = ServiceManager()
            self.component_status['services'] = 'healthy'
            print("✅ Service Manager initialized")
        except Exception as e:
            print(f"⚠️  Service Manager initialization failed: {e}")
            self.component_status['services'] = 'error'
            self.service_manager = None
        
        self.initialized = True
        print("✅ AI Manager initialized successfully")
        print(f"   Status: {self.component_status}")
    
    async def cleanup(self):
        """
        Cleanup resources
        """
        print("🧹 Cleaning up AI Manager...")
        
        if self.graph:
            try:
                self.graph.close()
                print("✅ Graph connection closed")
            except Exception as e:
                print(f"⚠️  Error closing graph: {e}")
        
        if self.service_manager:
            try:
                await self.service_manager.close()
                print("✅ Service Manager closed")
            except Exception as e:
                print(f"⚠️  Error closing service manager: {e}")
        
        self.initialized = False
        print("✅ AI Manager cleaned up")
    
    def get_recommendations(
        self,
        user_id: Optional[int] = None,
        user_sequence: Optional[List[int]] = None,
        query: Optional[str] = None,
        product_id: Optional[int] = None,
        k: int = 10,
        exclude_seen: bool = True,
        weights: Optional[Dict[str, float]] = None
    ) -> Tuple[List[Tuple[int, Dict[str, float]]], Dict[str, float]]:
        """
        Get recommendations using hybrid system
        
        Returns:
            Tuple of (recommendations, weights_used)
        """
        if not self.initialized or not self.hybrid:
            raise RuntimeError("AI Manager not initialized or hybrid not available")
        
        # Update weights if provided
        if weights:
            self.hybrid.set_weights(
                lstm=weights['lstm'],
                graph=weights['graph'],
                rag=weights['rag']
            )
        
        # Get recommendations
        recommendations = self.hybrid.recommend(
            user_id=user_id,
            user_sequence=user_sequence,
            query=query,
            product_id=product_id,
            k=k,
            exclude_seen=exclude_seen
        )
        
        return recommendations, self.hybrid.weights
    
    def get_chatbot_response(self, message: str) -> str:
        """
        Get chatbot response
        """
        if not self.initialized or not self.chatbot:
            raise RuntimeError("AI Manager not initialized or chatbot not available")
        
        return self.chatbot.chat(message)
    
    def get_similar_products(
        self,
        product_id: int,
        k: int = 10
    ) -> List[Tuple[int, Dict[str, float]]]:
        """
        Get similar products
        """
        if not self.initialized or not self.hybrid:
            raise RuntimeError("AI Manager not initialized or hybrid not available")
        
        return self.hybrid.recommend(
            product_id=product_id,
            k=k
        )
    
    def get_health_status(self) -> Dict[str, str]:
        """
        Get health status of all components
        """
        return self.component_status.copy()
    
    def get_stats(self) -> Dict:
        """
        Get statistics about the AI system
        """
        stats = {
            'total_products': 50,
            'total_users': 100,
            'total_interactions': 1731,
            'model_info': {}
        }
        
        # LSTM info
        if self.lstm:
            stats['model_info']['lstm'] = {
                'parameters': 241267,
                'vocab_size': 51,
                'embedding_dim': 64,
                'hidden_dim': 128
            }
        
        # Graph info
        if self.graph:
            try:
                graph_stats = self.graph.get_statistics()
                stats['model_info']['graph'] = graph_stats
            except:
                stats['model_info']['graph'] = {'status': 'error'}
        
        # RAG info
        if self.rag:
            stats['model_info']['rag'] = {
                'vectors': self.rag.index.ntotal if self.rag.index else 0,
                'embedding_dim': self.rag.embedding_dim,
                'model': 'paraphrase-multilingual-MiniLM-L12-v2'
            }
        
        return stats
    
    def explain_recommendation(
        self,
        product_id: int,
        score_breakdown: Dict[str, float]
    ) -> str:
        """
        Generate explanation for a recommendation
        """
        if not self.initialized or not self.hybrid:
            raise RuntimeError("AI Manager not initialized or hybrid not available")
        
        return self.hybrid.explain_recommendation(product_id, score_breakdown)
    
    async def get_smart_recommendations_for_user(
        self,
        user_id: int,
        k: int = 10,
        weights: Optional[Dict[str, float]] = None
    ) -> Tuple[List[Tuple[int, Dict[str, float]]], Dict]:
        """
        Get smart recommendations using user context from other services
        
        Args:
            user_id: User ID
            k: Number of recommendations
            weights: Custom weights
            
        Returns:
            Tuple of (recommendations, user_context)
        """
        if not self.service_manager:
            # Fallback to basic recommendations
            return self.get_recommendations(
                user_id=user_id,
                k=k,
                weights=weights
            ), {}
        
        # Get user context from other services
        context = await self.service_manager.get_smart_recommendations(user_id, k)
        
        # Get recommendations using interaction sequence
        recommendations, weights_used = self.get_recommendations(
            user_id=user_id,
            user_sequence=context.get("interaction_sequence", []),
            k=k,
            exclude_seen=True,
            weights=weights
        )
        
        return recommendations, context
    
    async def get_enriched_recommendations(
        self,
        user_id: Optional[int] = None,
        user_sequence: Optional[List[int]] = None,
        query: Optional[str] = None,
        product_id: Optional[int] = None,
        k: int = 10,
        exclude_seen: bool = True,
        weights: Optional[Dict[str, float]] = None,
        filter_available: bool = True
    ) -> Tuple[List[Dict], Dict[str, float]]:
        """
        Get recommendations enriched with product details
        
        Args:
            Same as get_recommendations, plus:
            filter_available: Filter out unavailable products
            
        Returns:
            Tuple of (enriched_recommendations, weights_used)
        """
        # Get basic recommendations
        recommendations, weights_used = self.get_recommendations(
            user_id=user_id,
            user_sequence=user_sequence,
            query=query,
            product_id=product_id,
            k=k * 2 if filter_available else k,  # Get more if filtering
            exclude_seen=exclude_seen,
            weights=weights
        )
        
        # Filter available products if requested
        if filter_available and self.service_manager:
            recommendations = await self.service_manager.filter_available_recommendations(
                recommendations
            )
            recommendations = recommendations[:k]  # Trim to k
        
        # Enrich with product details
        if self.service_manager:
            enriched = await self.service_manager.enrich_recommendations(recommendations)
        else:
            # Basic enrichment without service manager
            enriched = [
                {
                    "product_id": pid,
                    "score": scores.get("final_score", 0.0),
                    "breakdown": {
                        "lstm": scores.get("lstm", 0.0),
                        "graph": scores.get("graph", 0.0),
                        "rag": scores.get("rag", 0.0)
                    },
                    "product": {
                        "name": f"Product {pid}",
                        "category": "Unknown",
                        "price": 0,
                        "image": "",
                        "stock": 0
                    }
                }
                for pid, scores in recommendations
            ]
        
        return enriched, weights_used
