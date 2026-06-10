"""
Run Phase 5: Hybrid Recommendation System
This script combines LSTM, Knowledge Graph, and RAG recommendations
"""
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from lstm_model import LSTMRecommender
from graph import ProductKnowledgeGraph
from rag import ProductRAG, load_products_from_csv
from hybrid import HybridRecommender

def main():
    print("=" * 70)
    print("📌 GIAI ĐOẠN 5 — HỆ THỐNG GỢI Ý KẾT HỢP")
    print("=" * 70)
    
    # Task 5.1: Load all three models
    print("\n" + "=" * 70)
    print("Nhiệm vụ 5.1: Tải các mô hình")
    print("=" * 70)
    
    # Load LSTM
    print("\n📊 Đang tải LSTM Recommender...")
    try:
        lstm = LSTMRecommender(
            model_path='models/lstm_model_best.pth',
            mappings_path='data/mappings.pkl'
        )
        print("✅ LSTM loaded successfully")
    except Exception as e:
        print(f"⚠️  LSTM load failed: {e}")
        lstm = None
    
    # Load Knowledge Graph
    print("\n🕸️  Đang kết nối Knowledge Graph...")
    try:
        graph = ProductKnowledgeGraph(
            uri="bolt://localhost:7687",
            user="neo4j",
            password="password123"
        )
        print("✅ Graph connected successfully")
    except Exception as e:
        print(f"⚠️  Graph connection failed: {e}")
        print("   Đảm bảo Neo4j đang chạy: docker compose -f docker-compose.neo4j.yml up -d")
        graph = None
    
    # Load RAG
    print("\n🔍 Đang tải RAG System...")
    try:
        rag = ProductRAG()
        rag.load(
            index_path='data/faiss_index.bin',
            metadata_path='data/rag_metadata.pkl'
        )
        print("✅ RAG loaded successfully")
    except Exception as e:
        print(f"⚠️  RAG load failed: {e}")
        rag = None
    
    # Task 5.2: Initialize Hybrid Recommender
    print("\n" + "=" * 70)
    print("Nhiệm vụ 5.2: Khởi tạo Hybrid Recommender")
    print("=" * 70)
    
    hybrid = HybridRecommender(
        lstm_recommender=lstm,
        graph_recommender=graph,
        rag_recommender=rag,
        weights={
            'lstm': 0.3,   # Sequential behavior patterns
            'graph': 0.3,  # Relationship-based
            'rag': 0.4     # Semantic similarity
        }
    )
    
    # Task 5.3: Test Hybrid Recommendations
    print("\n" + "=" * 70)
    print("Nhiệm vụ 5.3: Kiểm tra gợi ý kết hợp")
    print("=" * 70)
    
    # Test Case 1: User-based recommendation
    print("\n" + "=" * 70)
    print("Test 1: Gợi ý dựa trên lịch sử người dùng")
    print("=" * 70)
    
    user_id = 1
    user_sequence = [1, 2, 3, 4, 5]  # iPhone, Samsung, iPad, Xiaomi, OPPO
    
    print(f"\nUser ID: {user_id}")
    print(f"Lịch sử xem: {user_sequence}")
    
    recommendations = hybrid.recommend(
        user_id=user_id,
        user_sequence=user_sequence,
        k=10,
        exclude_seen=True
    )
    
    print(f"\n🎯 Top-10 Gợi ý:")
    print("-" * 70)
    for i, (pid, scores) in enumerate(recommendations, 1):
        print(f"\n{i}. Sản phẩm {pid}")
        print(f"   Điểm cuối: {scores['final_score']:.4f}")
        print(f"   LSTM: {scores['lstm']:.4f} | Graph: {scores['graph']:.4f} | RAG: {scores['rag']:.4f}")
    
    # Test Case 2: Query-based recommendation
    print("\n" + "=" * 70)
    print("Test 2: Gợi ý dựa trên truy vấn văn bản")
    print("=" * 70)
    
    query = "laptop gaming mạnh mẽ cho sinh viên"
    
    print(f"\nTruy vấn: '{query}'")
    
    recommendations = hybrid.recommend(
        query=query,
        k=10
    )
    
    print(f"\n🎯 Top-10 Gợi ý:")
    print("-" * 70)
    for i, (pid, scores) in enumerate(recommendations, 1):
        print(f"\n{i}. Sản phẩm {pid}")
        print(f"   Điểm cuối: {scores['final_score']:.4f}")
        print(f"   LSTM: {scores['lstm']:.4f} | Graph: {scores['graph']:.4f} | RAG: {scores['rag']:.4f}")
    
    # Test Case 3: Product-based recommendation
    print("\n" + "=" * 70)
    print("Test 3: Gợi ý sản phẩm tương tự")
    print("=" * 70)
    
    product_id = 1  # iPhone 15 Pro Max
    
    print(f"\nSản phẩm gốc: {product_id}")
    
    recommendations = hybrid.recommend(
        product_id=product_id,
        k=10
    )
    
    print(f"\n🎯 Top-10 Sản phẩm tương tự:")
    print("-" * 70)
    for i, (pid, scores) in enumerate(recommendations, 1):
        print(f"\n{i}. Sản phẩm {pid}")
        print(f"   Điểm cuối: {scores['final_score']:.4f}")
        print(f"   LSTM: {scores['lstm']:.4f} | Graph: {scores['graph']:.4f} | RAG: {scores['rag']:.4f}")
    
    # Test Case 4: Combined recommendation (user + query)
    print("\n" + "=" * 70)
    print("Test 4: Gợi ý kết hợp (người dùng + truy vấn)")
    print("=" * 70)
    
    user_id = 5
    user_sequence = [6, 7, 8]  # MacBook, Dell, ASUS
    query = "tai nghe bluetooth chất lượng cao"
    
    print(f"\nUser ID: {user_id}")
    print(f"Lịch sử: {user_sequence}")
    print(f"Truy vấn: '{query}'")
    
    recommendations = hybrid.recommend(
        user_id=user_id,
        user_sequence=user_sequence,
        query=query,
        k=10,
        exclude_seen=True
    )
    
    print(f"\n🎯 Top-10 Gợi ý:")
    print("-" * 70)
    for i, (pid, scores) in enumerate(recommendations, 1):
        print(f"\n{i}. Sản phẩm {pid}")
        print(f"   Điểm cuối: {scores['final_score']:.4f}")
        print(f"   LSTM: {scores['lstm']:.4f} | Graph: {scores['graph']:.4f} | RAG: {scores['rag']:.4f}")
    
    # Task 5.4: Test different weight configurations
    print("\n" + "=" * 70)
    print("Nhiệm vụ 5.4: Kiểm tra các cấu hình trọng số khác nhau")
    print("=" * 70)
    
    test_weights = [
        {'lstm': 0.5, 'graph': 0.3, 'rag': 0.2, 'name': 'LSTM-focused'},
        {'lstm': 0.2, 'graph': 0.5, 'rag': 0.3, 'name': 'Graph-focused'},
        {'lstm': 0.2, 'graph': 0.2, 'rag': 0.6, 'name': 'RAG-focused'},
        {'lstm': 0.33, 'graph': 0.33, 'rag': 0.34, 'name': 'Balanced'},
    ]
    
    test_sequence = [1, 2, 3]
    
    print(f"\nKiểm tra với chuỗi: {test_sequence}")
    print("\nSo sánh top-5 gợi ý với các trọng số khác nhau:")
    print("=" * 70)
    
    for config in test_weights:
        print(f"\n📊 Cấu hình: {config['name']}")
        print(f"   Trọng số: LSTM={config['lstm']:.2f}, Graph={config['graph']:.2f}, RAG={config['rag']:.2f}")
        
        hybrid.set_weights(
            lstm=config['lstm'],
            graph=config['graph'],
            rag=config['rag']
        )
        
        recs = hybrid.recommend(
            user_sequence=test_sequence,
            k=5,
            exclude_seen=True
        )
        
        print(f"   Top-5: {[pid for pid, _ in recs]}")
    
    # Task 5.5: Generate explanations
    print("\n" + "=" * 70)
    print("Nhiệm vụ 5.5: Tạo giải thích cho gợi ý")
    print("=" * 70)
    
    # Reset to default weights
    hybrid.set_weights(lstm=0.3, graph=0.3, rag=0.4)
    
    # Get recommendations
    recs = hybrid.recommend(
        user_sequence=[1, 2, 3],
        k=5,
        exclude_seen=True
    )
    
    print("\n📝 Giải thích chi tiết cho top-5 gợi ý:")
    print("=" * 70)
    
    for i, (pid, scores) in enumerate(recs, 1):
        explanation = hybrid.explain_recommendation(pid, scores)
        print(f"\n{i}. {explanation}")
    
    # Save configuration
    print("\n" + "=" * 70)
    print("💾 Lưu cấu hình")
    print("=" * 70)
    
    hybrid.save_config('data/hybrid_config.pkl')
    
    # Close connections
    if graph:
        graph.close()
    
    print("\n" + "=" * 70)
    print("✅ GIAI ĐOẠN 5 HOÀN THÀNH!")
    print("=" * 70)
    print("\nHệ thống gợi ý kết hợp cung cấp:")
    print("   ✅ Kết hợp 3 nguồn gợi ý (LSTM + Graph + RAG)")
    print("   ✅ Chuẩn hóa và kết hợp điểm số")
    print("   ✅ Trọng số có thể cấu hình")
    print("   ✅ Giải thích cho gợi ý")
    print("   ✅ Hỗ trợ nhiều loại truy vấn")
    print("\nSẵn sàng cho:")
    print("   - Giai đoạn 6: Dịch vụ FastAPI")
    print("   - Giai đoạn 7: Tích hợp với các microservices")

if __name__ == '__main__':
    main()
