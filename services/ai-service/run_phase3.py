t"""
Run Phase 3: Knowledge Graph (Neo4j)
This script sets up Neo4j and builds the knowledge graph
"""
import sys
import os
import time
import subprocess

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def start_neo4j():
    """Start Neo4j using Docker Compose"""
    print("=" * 70)
    print("🐳 Starting Neo4j Docker Container")
    print("=" * 70)
    
    # Check if Neo4j is already running
    result = subprocess.run(
        ['docker', 'ps', '--filter', 'name=neo4j-graph', '--format', '{{.Names}}'],
        capture_output=True,
        text=True
    )
    
    if 'neo4j-graph' in result.stdout:
        print("✅ Neo4j container already running")
        return True
    
    # Start Neo4j
    print("Starting Neo4j container...")
    result = subprocess.run(
        ['docker', 'compose', '-f', 'docker-compose.neo4j.yml', 'up', '-d'],
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        print(f"❌ Failed to start Neo4j: {result.stderr}")
        return False
    
    print("✅ Neo4j container started")
    print("   HTTP: http://localhost:7474")
    print("   Bolt: bolt://localhost:7687")
    print("   Username: neo4j")
    print("   Password: password123")
    
    # Wait for Neo4j to be ready
    print("\n⏳ Waiting for Neo4j to be ready...")
    max_retries = 30
    for i in range(max_retries):
        try:
            from neo4j import GraphDatabase
            driver = GraphDatabase.driver(
                "bolt://localhost:7687",
                auth=("neo4j", "password123")
            )
            with driver.session() as session:
                session.run("RETURN 1")
            driver.close()
            print("✅ Neo4j is ready!")
            return True
        except Exception as e:
            if i < max_retries - 1:
                print(f"   Attempt {i+1}/{max_retries}... waiting")
                time.sleep(2)
            else:
                print(f"❌ Neo4j failed to start: {e}")
                return False
    
    return False

def main():
    print("=" * 70)
    print("📌 PHASE 3 — KNOWLEDGE GRAPH (Neo4j)")
    print("=" * 70)
    
    # Start Neo4j
    if not start_neo4j():
        print("\n❌ Failed to start Neo4j. Please check Docker.")
        return
    
    # Build knowledge graph
    print("\n" + "=" * 70)
    print("🏗️  Building Knowledge Graph")
    print("=" * 70)
    
    from graph import build_knowledge_graph
    
    try:
        graph = build_knowledge_graph(
            csv_path='data/user_behavior.csv',
            mappings_path='data/mappings.pkl',
            clear_existing=True
        )
        
        # Test recommendations
        print("\n" + "=" * 70)
        print("🧪 Testing Graph Recommendations")
        print("=" * 70)
        
        # Test 1: User-based recommendations
        print("\n1️⃣  User-based Recommendations:")
        for user_id in [1, 5, 10]:
            recs = graph.recommend_by_user_history(user_id, k=5)
            print(f"\n   User {user_id}:")
            if recs:
                for i, (product_id, score) in enumerate(recs, 1):
                    print(f"      {i}. Product {product_id} (score: {score:.1f})")
            else:
                print("      No recommendations found")
        
        # Test 2: Category-based recommendations
        print("\n2️⃣  Category-based Recommendations:")
        for product_id in [1, 10, 20]:
            recs = graph.recommend_by_category(product_id, k=5)
            print(f"\n   Product {product_id}:")
            if recs:
                for i, (pid, score) in enumerate(recs, 1):
                    print(f"      {i}. Product {pid} (score: {score:.1f})")
            else:
                print("      No recommendations found")
        
        # Test 3: Similarity-based recommendations
        print("\n3️⃣  Similarity-based Recommendations:")
        for product_id in [1, 10, 20]:
            recs = graph.recommend_similar_products(product_id, k=5)
            print(f"\n   Product {product_id}:")
            if recs:
                for i, (pid, score) in enumerate(recs, 1):
                    print(f"      {i}. Product {pid} (score: {score:.1f})")
            else:
                print("      No similar products found")
        
        # Close connection
        graph.close()
        
        print("\n" + "=" * 70)
        print("✅ PHASE 3 COMPLETE!")
        print("=" * 70)
        print("\nKnowledge Graph is ready!")
        print("   - Neo4j Browser: http://localhost:7474")
        print("   - Bolt connection: bolt://localhost:7687")
        print("   - Username: neo4j")
        print("   - Password: password123")
        print("\nGraph provides:")
        print("   ✅ User-based recommendations")
        print("   ✅ Category-based recommendations")
        print("   ✅ Similarity-based recommendations")
        print("\nReady for:")
        print("   - Phase 4: RAG System")
        print("   - Phase 5: Hybrid Recommendation")
        
    except Exception as e:
        print(f"\n❌ Error building graph: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
