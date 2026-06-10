"""
Knowledge Graph for Product Recommendation using Neo4j
Manages relationships between users and products
"""
from neo4j import GraphDatabase
import pandas as pd
import numpy as np
from typing import List, Dict, Tuple, Optional
import pickle

class ProductKnowledgeGraph:
    """
    Knowledge Graph for product recommendations
    
    Nodes:
    - User: Represents a user
    - Product: Represents a product
    
    Relationships:
    - (User)-[:VIEWED]->(Product)
    - (User)-[:ADDED_TO_CART]->(Product)
    - (User)-[:PURCHASED]->(Product)
    - (Product)-[:SIMILAR_TO]->(Product)
    - (Product)-[:IN_CATEGORY]->(Category)
    """
    
    def __init__(
        self,
        uri: str = "bolt://localhost:7687",
        user: str = "neo4j",
        password: str = "password123"
    ):
        """
        Initialize Neo4j connection
        
        Args:
            uri: Neo4j connection URI
            user: Username
            password: Password
        """
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        print(f"✅ Connected to Neo4j at {uri}")
    
    def close(self):
        """Close Neo4j connection"""
        self.driver.close()
        print("✅ Closed Neo4j connection")
    
    def clear_database(self):
        """Clear all nodes and relationships"""
        with self.driver.session() as session:
            session.run("MATCH (n) DETACH DELETE n")
        print("✅ Cleared database")
    
    def create_constraints(self):
        """Create uniqueness constraints"""
        with self.driver.session() as session:
            # User constraint
            session.run("""
                CREATE CONSTRAINT user_id IF NOT EXISTS
                FOR (u:User) REQUIRE u.user_id IS UNIQUE
            """)
            
            # Product constraint
            session.run("""
                CREATE CONSTRAINT product_id IF NOT EXISTS
                FOR (p:Product) REQUIRE p.product_id IS UNIQUE
            """)
            
            # Category constraint
            session.run("""
                CREATE CONSTRAINT category_name IF NOT EXISTS
                FOR (c:Category) REQUIRE c.name IS UNIQUE
            """)
        
        print("✅ Created constraints")
    
    def create_indexes(self):
        """Create indexes for better query performance"""
        with self.driver.session() as session:
            # Index on product category
            session.run("""
                CREATE INDEX product_category IF NOT EXISTS
                FOR (p:Product) ON (p.category)
            """)
        
        print("✅ Created indexes")
    
    def load_user_behavior(self, csv_path: str = 'data/user_behavior.csv'):
        """
        Load user behavior data and create graph
        
        Args:
            csv_path: Path to user behavior CSV
        """
        print(f"\n📂 Loading user behavior from {csv_path}...")
        df = pd.read_csv(csv_path)
        print(f"   Loaded {len(df)} interactions")
        
        # Create users
        print("\n👥 Creating User nodes...")
        unique_users = df['user_id'].unique()
        with self.driver.session() as session:
            for user_id in unique_users:
                session.run("""
                    MERGE (u:User {user_id: $user_id})
                """, user_id=int(user_id))
        print(f"   Created {len(unique_users)} users")
        
        # Create products
        print("\n📦 Creating Product nodes...")
        unique_products = df['product_id'].unique()
        with self.driver.session() as session:
            for product_id in unique_products:
                session.run("""
                    MERGE (p:Product {product_id: $product_id})
                """, product_id=int(product_id))
        print(f"   Created {len(unique_products)} products")
        
        # Create relationships based on actions
        print("\n🔗 Creating relationships...")
        
        # Group by action type
        action_counts = {}
        
        for action in ['view', 'add_to_cart', 'purchase']:
            action_df = df[df['action'] == action]
            action_counts[action] = len(action_df)
            
            # Map action to relationship type
            rel_type_map = {
                'view': 'VIEWED',
                'add_to_cart': 'ADDED_TO_CART',
                'purchase': 'PURCHASED'
            }
            rel_type = rel_type_map[action]
            
            # Create relationships in batches
            batch_size = 1000
            for i in range(0, len(action_df), batch_size):
                batch = action_df.iloc[i:i+batch_size]
                
                with self.driver.session() as session:
                    for _, row in batch.iterrows():
                        session.run(f"""
                            MATCH (u:User {{user_id: $user_id}})
                            MATCH (p:Product {{product_id: $product_id}})
                            MERGE (u)-[r:{rel_type}]->(p)
                            ON CREATE SET r.timestamp = $timestamp
                        """, 
                        user_id=int(row['user_id']),
                        product_id=int(row['product_id']),
                        timestamp=row['timestamp'])
            
            print(f"   Created {action_counts[action]} {rel_type} relationships")
        
        print(f"\n✅ Graph created successfully!")
        print(f"   Total relationships: {sum(action_counts.values())}")
    
    def create_product_categories(self, mappings_path: str = 'data/mappings.pkl'):
        """
        Create category nodes and relationships
        
        Args:
            mappings_path: Path to product mappings
        """
        print("\n📁 Creating product categories...")
        
        # Define categories (matching our seeded data)
        categories = {
            'Điện thoại & Tablet': list(range(1, 6)),
            'Laptop & Máy tính': list(range(6, 11)),
            'Âm thanh & Phụ kiện': list(range(11, 16)),
            'Thời trang Nam': list(range(16, 21)),
            'Thời trang Nữ': list(range(21, 26)),
            'Đồ gia dụng': list(range(26, 31)),
            'Sách & Văn phòng phẩm': list(range(31, 36)),
            'Thể thao & Du lịch': list(range(36, 41)),
            'Mẹ & Bé': list(range(41, 46)),
            'Làm đẹp & Sức khỏe': list(range(46, 51)),
        }
        
        with self.driver.session() as session:
            for category_name, product_ids in categories.items():
                # Create category node
                session.run("""
                    MERGE (c:Category {name: $name})
                """, name=category_name)
                
                # Link products to category
                for product_id in product_ids:
                    session.run("""
                        MATCH (p:Product {product_id: $product_id})
                        MATCH (c:Category {name: $category})
                        MERGE (p)-[:IN_CATEGORY]->(c)
                        SET p.category = $category
                    """, product_id=product_id, category=category_name)
        
        print(f"   Created {len(categories)} categories")
        print(f"   Linked products to categories")
    
    def create_similarity_relationships(self, threshold: float = 0.3):
        """
        Create SIMILAR_TO relationships between products
        Based on co-occurrence in user behavior
        
        Args:
            threshold: Minimum similarity score
        """
        print(f"\n🔗 Creating product similarity relationships (threshold={threshold})...")
        
        with self.driver.session() as session:
            # Find products that are frequently viewed together
            result = session.run("""
                MATCH (u:User)-[:VIEWED]->(p1:Product)
                MATCH (u)-[:VIEWED]->(p2:Product)
                WHERE p1.product_id < p2.product_id
                WITH p1, p2, COUNT(DISTINCT u) as co_occurrence
                WHERE co_occurrence >= 3
                RETURN p1.product_id as product1, p2.product_id as product2, co_occurrence
                ORDER BY co_occurrence DESC
                LIMIT 200
            """)
            
            similarities = list(result)
            
            # Create SIMILAR_TO relationships
            for record in similarities:
                session.run("""
                    MATCH (p1:Product {product_id: $product1})
                    MATCH (p2:Product {product_id: $product2})
                    MERGE (p1)-[s:SIMILAR_TO]->(p2)
                    SET s.score = $score
                    MERGE (p2)-[s2:SIMILAR_TO]->(p1)
                    SET s2.score = $score
                """, 
                product1=record['product1'],
                product2=record['product2'],
                score=float(record['co_occurrence']))
        
        print(f"   Created {len(similarities) * 2} similarity relationships")
    
    def get_statistics(self) -> Dict:
        """Get graph statistics"""
        with self.driver.session() as session:
            # Count nodes
            user_count = session.run("MATCH (u:User) RETURN COUNT(u) as count").single()['count']
            product_count = session.run("MATCH (p:Product) RETURN COUNT(p) as count").single()['count']
            category_count = session.run("MATCH (c:Category) RETURN COUNT(c) as count").single()['count']
            
            # Count relationships
            viewed_count = session.run("MATCH ()-[r:VIEWED]->() RETURN COUNT(r) as count").single()['count']
            cart_count = session.run("MATCH ()-[r:ADDED_TO_CART]->() RETURN COUNT(r) as count").single()['count']
            purchase_count = session.run("MATCH ()-[r:PURCHASED]->() RETURN COUNT(r) as count").single()['count']
            similar_count = session.run("MATCH ()-[r:SIMILAR_TO]->() RETURN COUNT(r) as count").single()['count']
            category_count_rel = session.run("MATCH ()-[r:IN_CATEGORY]->() RETURN COUNT(r) as count").single()['count']
        
        stats = {
            'nodes': {
                'users': user_count,
                'products': product_count,
                'categories': category_count,
                'total': user_count + product_count + category_count
            },
            'relationships': {
                'viewed': viewed_count,
                'added_to_cart': cart_count,
                'purchased': purchase_count,
                'similar_to': similar_count,
                'in_category': category_count_rel,
                'total': viewed_count + cart_count + purchase_count + similar_count + category_count_rel
            }
        }
        
        return stats
    
    def print_statistics(self):
        """Print graph statistics"""
        stats = self.get_statistics()
        
        print("\n📊 Graph Statistics:")
        print("=" * 60)
        print("Nodes:")
        for node_type, count in stats['nodes'].items():
            print(f"   {node_type.capitalize()}: {count}")
        
        print("\nRelationships:")
        for rel_type, count in stats['relationships'].items():
            print(f"   {rel_type.upper()}: {count}")
        print("=" * 60)
    
    def recommend_by_user_history(
        self,
        user_id: int,
        k: int = 10
    ) -> List[Tuple[int, float]]:
        """
        Recommend products based on user's purchase history
        Uses collaborative filtering through the graph
        
        Args:
            user_id: User ID
            k: Number of recommendations
            
        Returns:
            List of (product_id, score) tuples
        """
        with self.driver.session() as session:
            result = session.run("""
                // Find products the user has interacted with
                MATCH (u:User {user_id: $user_id})-[r:VIEWED|ADDED_TO_CART|PURCHASED]->(p:Product)
                
                // Find similar products
                MATCH (p)-[:SIMILAR_TO]->(rec:Product)
                
                // Exclude products user already interacted with
                WHERE NOT (u)-[:VIEWED|ADDED_TO_CART|PURCHASED]->(rec)
                
                // Calculate recommendation score
                WITH rec, COUNT(DISTINCT p) as similarity_count
                
                RETURN rec.product_id as product_id, similarity_count as score
                ORDER BY score DESC
                LIMIT $k
            """, user_id=user_id, k=k)
            
            recommendations = [
                (record['product_id'], float(record['score']))
                for record in result
            ]
        
        return recommendations
    
    def recommend_by_category(
        self,
        product_id: int,
        k: int = 10
    ) -> List[Tuple[int, float]]:
        """
        Recommend products from the same category
        
        Args:
            product_id: Product ID
            k: Number of recommendations
            
        Returns:
            List of (product_id, score) tuples
        """
        with self.driver.session() as session:
            result = session.run("""
                // Find the product's category
                MATCH (p:Product {product_id: $product_id})-[:IN_CATEGORY]->(c:Category)
                
                // Find other products in the same category
                MATCH (rec:Product)-[:IN_CATEGORY]->(c)
                WHERE rec.product_id <> $product_id
                
                // Count how many users purchased each product
                OPTIONAL MATCH (u:User)-[:PURCHASED]->(rec)
                WITH rec, COUNT(DISTINCT u) as purchase_count
                
                RETURN rec.product_id as product_id, purchase_count as score
                ORDER BY score DESC
                LIMIT $k
            """, product_id=product_id, k=k)
            
            recommendations = [
                (record['product_id'], float(record['score']))
                for record in result
            ]
        
        return recommendations
    
    def recommend_similar_products(
        self,
        product_id: int,
        k: int = 10
    ) -> List[Tuple[int, float]]:
        """
        Recommend similar products based on SIMILAR_TO relationships
        
        Args:
            product_id: Product ID
            k: Number of recommendations
            
        Returns:
            List of (product_id, score) tuples
        """
        with self.driver.session() as session:
            result = session.run("""
                MATCH (p:Product {product_id: $product_id})-[s:SIMILAR_TO]->(rec:Product)
                RETURN rec.product_id as product_id, s.score as score
                ORDER BY score DESC
                LIMIT $k
            """, product_id=product_id, k=k)
            
            recommendations = [
                (record['product_id'], float(record['score']))
                for record in result
            ]
        
        return recommendations


def build_knowledge_graph(
    csv_path: str = 'data/user_behavior.csv',
    mappings_path: str = 'data/mappings.pkl',
    clear_existing: bool = True
) -> ProductKnowledgeGraph:
    """
    Build complete knowledge graph
    
    Args:
        csv_path: Path to user behavior CSV
        mappings_path: Path to product mappings
        clear_existing: Whether to clear existing data
        
    Returns:
        ProductKnowledgeGraph instance
    """
    print("=" * 70)
    print("🚀 Building Knowledge Graph")
    print("=" * 70)
    
    # Initialize graph
    graph = ProductKnowledgeGraph()
    
    # Clear existing data if requested
    if clear_existing:
        graph.clear_database()
    
    # Create constraints and indexes
    graph.create_constraints()
    graph.create_indexes()
    
    # Load user behavior
    graph.load_user_behavior(csv_path)
    
    # Create categories
    graph.create_product_categories(mappings_path)
    
    # Create similarity relationships
    graph.create_similarity_relationships(threshold=0.3)
    
    # Print statistics
    graph.print_statistics()
    
    print("\n✅ Knowledge Graph built successfully!")
    
    return graph


if __name__ == '__main__':
    # Build graph
    graph = build_knowledge_graph()
    
    # Test recommendations
    print("\n" + "=" * 70)
    print("🧪 Testing Recommendations")
    print("=" * 70)
    
    # Test user-based recommendations
    test_user_id = 1
    print(f"\nUser {test_user_id} recommendations:")
    recs = graph.recommend_by_user_history(test_user_id, k=5)
    for i, (product_id, score) in enumerate(recs, 1):
        print(f"   {i}. Product {product_id} (score: {score})")
    
    # Test category-based recommendations
    test_product_id = 5
    print(f"\nCategory recommendations for Product {test_product_id}:")
    recs = graph.recommend_by_category(test_product_id, k=5)
    for i, (product_id, score) in enumerate(recs, 1):
        print(f"   {i}. Product {product_id} (score: {score})")
    
    # Test similarity-based recommendations
    print(f"\nSimilar products to Product {test_product_id}:")
    recs = graph.recommend_similar_products(test_product_id, k=5)
    for i, (product_id, score) in enumerate(recs, 1):
        print(f"   {i}. Product {product_id} (score: {score})")
    
    # Close connection
    graph.close()
