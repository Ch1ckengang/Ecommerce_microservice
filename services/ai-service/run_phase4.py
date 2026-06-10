"""
Run Phase 4: RAG System
This script builds the RAG system with vector search
"""
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from rag import ProductRAG, ProductChatbot, load_products_from_csv

def main():
    print("=" * 70)
    print("📌 PHASE 4 — RAG SYSTEM")
    print("=" * 70)
    
    # Task 4.1: Generate embeddings
    print("\n" + "=" * 70)
    print("Task 4.1: Generate Embeddings")
    print("=" * 70)
    
    # Load products
    products = load_products_from_csv('data/user_behavior.csv')
    
    # Initialize RAG
    rag = ProductRAG(
        model_name='paraphrase-multilingual-MiniLM-L12-v2',
        embedding_dim=384
    )
    
    # Task 4.2 & 4.3: Setup vector database and store embeddings
    print("\n" + "=" * 70)
    print("Task 4.2 & 4.3: Setup FAISS and Store Embeddings")
    print("=" * 70)
    
    rag.build_index(products, use_gpu=False)
    
    # Task 4.4: Retrieval
    print("\n" + "=" * 70)
    print("Task 4.4: Test Retrieval")
    print("=" * 70)
    
    test_queries = [
        "điện thoại iPhone cao cấp",
        "laptop gaming mạnh mẽ",
        "tai nghe không dây chống ồn",
        "đồ gia dụng nhà bếp",
        "sách văn phòng phẩm"
    ]
    
    for query in test_queries:
        print(f"\n🔍 Query: '{query}'")
        results = rag.search(query, k=3)
        
        if results:
            print("   Top 3 results:")
            for i, (pid, score, product) in enumerate(results, 1):
                print(f"      {i}. Product {pid}: {product['name']}")
                print(f"         Score: {score:.4f}")
                print(f"         Category: {product['category']}")
        else:
            print("   No results found")
    
    # Test product-based recommendations
    print("\n" + "=" * 70)
    print("Product-based Recommendations")
    print("=" * 70)
    
    test_products = [1, 6, 11]
    for pid in test_products:
        product = next((p for p in products if p['product_id'] == pid), None)
        if product:
            print(f"\n📦 Similar to: {product['name']}")
            recs = rag.recommend_by_product(pid, k=5)
            
            if recs:
                print("   Top 5 similar products:")
                for i, (rec_pid, score) in enumerate(recs, 1):
                    rec_product = next((p for p in products if p['product_id'] == rec_pid), None)
                    if rec_product:
                        print(f"      {i}. Product {rec_pid}: {rec_product['name']} (score: {score:.4f})")
    
    # Task 4.5: Generate response (Chatbot)
    print("\n" + "=" * 70)
    print("Task 4.5: Chatbot Response Generation")
    print("=" * 70)
    
    chatbot = ProductChatbot(rag)
    
    test_conversations = [
        "Xin chào",
        "Tôi muốn mua điện thoại iPhone",
        "Laptop cho sinh viên giá rẻ",
        "Tai nghe bluetooth tốt nhất",
        "Gợi ý sản phẩm tương tự product 1"
    ]
    
    print("\n💬 Chatbot Conversation:")
    print("-" * 70)
    
    for message in test_conversations:
        print(f"\n👤 User: {message}")
        response = chatbot.chat(message)
        print(f"🤖 Bot:\n{response}")
        print("-" * 70)
    
    # Save RAG system
    print("\n" + "=" * 70)
    print("💾 Saving RAG System")
    print("=" * 70)
    
    rag.save(
        index_path='data/faiss_index.bin',
        metadata_path='data/rag_metadata.pkl'
    )
    
    print("\n" + "=" * 70)
    print("✅ PHASE 4 COMPLETE!")
    print("=" * 70)
    print("\nGenerated files:")
    print("   📄 data/faiss_index.bin - FAISS vector index")
    print("   📄 data/rag_metadata.pkl - Product metadata")
    print("\nRAG System provides:")
    print("   ✅ Semantic product search")
    print("   ✅ Vector similarity recommendations")
    print("   ✅ Chatbot consultation")
    print("\nReady for:")
    print("   - Phase 5: Hybrid Recommendation")
    print("   - Phase 6: FastAPI Service Integration")

if __name__ == '__main__':
    main()
