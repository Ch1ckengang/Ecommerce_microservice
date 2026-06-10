#!/usr/bin/env python3
"""
Quick script to load product data into Neo4j
Run from host machine (not in container)
"""

import requests
from neo4j import GraphDatabase
import time

# Configuration
NEO4J_URI = "bolt://neo4j:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "password123"
PRODUCT_SERVICE_URL = "http://product-service:8000/products/"

def get_products():
    """Fetch products from Product Service"""
    try:
        response = requests.get(PRODUCT_SERVICE_URL, timeout=5)
        response.raise_for_status()
        data = response.json()
        products = data.get('data', [])  # Changed from 'results' to 'data'
        print(f"✅ Fetched {len(products)} products from Product Service")
        return products
    except Exception as e:
        print(f"❌ Error fetching products: {e}")
        return []

def load_to_neo4j(products):
    """Load products into Neo4j"""
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
    
    try:
        with driver.session() as session:
            # Clear existing data
            print("🧹 Clearing existing Neo4j data...")
            session.run("MATCH (n) DETACH DELETE n")
            
            # Create products
            print(f"📊 Creating {len(products)} product nodes...")
            for product in products:
                category_name = product.get('category', {}).get('name', 'Unknown') if isinstance(product.get('category'), dict) else 'Unknown'
                session.run("""
                    CREATE (p:Product {
                        product_id: $product_id,
                        name: $name,
                        price: $price,
                        category: $category,
                        stock: $stock,
                        description: $description
                    })
                """, 
                    product_id=product['id'],
                    name=product['name'],
                    price=float(product['price']),
                    category=category_name,
                    stock=product.get('stock', 0),
                    description=product.get('description', '')
                )
            
            print("✅ Products created")
            
            # Create categories
            print("📁 Creating category nodes...")
            categories = list(set(
                p.get('category', {}).get('name', 'Unknown') if isinstance(p.get('category'), dict) else 'Unknown'
                for p in products
            ))
            for category in categories:
                session.run("""
                    CREATE (c:Category {name: $name})
                """, name=category)
            
            print(f"✅ Created {len(categories)} categories")
            
            # Link products to categories
            print("🔗 Linking products to categories...")
            session.run("""
                MATCH (p:Product), (c:Category)
                WHERE p.category = c.name
                CREATE (p)-[:IN_CATEGORY]->(c)
            """)
            
            print("✅ Products linked to categories")
            
            # Compute product similarity (same category)
            print("🔍 Computing product similarities...")
            result = session.run("""
                MATCH (p1:Product), (p2:Product)
                WHERE p1.category = p2.category 
                  AND p1.product_id < p2.product_id
                  AND abs(p1.price - p2.price) < p1.price * 0.5
                CREATE (p1)-[:SIMILAR_TO {score: 0.8}]->(p2)
                CREATE (p2)-[:SIMILAR_TO {score: 0.8}]->(p1)
                RETURN count(*) as relationships_created
            """)
            
            similarity_count = result.single()['relationships_created']
            print(f"✅ Created {similarity_count} similarity relationships")
            
            # Create indexes
            print("📇 Creating indexes...")
            session.run("CREATE INDEX product_id_index IF NOT EXISTS FOR (p:Product) ON (p.product_id)")
            session.run("CREATE INDEX category_index IF NOT EXISTS FOR (p:Product) ON (p.category)")
            print("✅ Indexes created")
            
            # Statistics
            print("\n📊 NEO4J STATISTICS")
            print("="*50)
            
            stats = session.run("""
                MATCH (n)
                RETURN labels(n)[0] as type, count(n) as count
                ORDER BY count DESC
            """)
            
            for record in stats:
                print(f"   {record['type']}: {record['count']}")
            
            rel_stats = session.run("""
                MATCH ()-[r]->()
                RETURN type(r) as relationship, count(r) as count
                ORDER BY count DESC
            """)
            
            print("\n   Relationships:")
            for record in rel_stats:
                print(f"   {record['relationship']}: {record['count']}")
            
    finally:
        driver.close()

def main():
    print("\n" + "="*70)
    print("🕸️  NEO4J KNOWLEDGE GRAPH - DATA LOADER")
    print("="*70 + "\n")
    
    # Fetch products
    products = get_products()
    
    if not products:
        print("❌ No products found. Make sure Product Service is running.")
        return
    
    # Load to Neo4j
    print(f"\n📤 Loading {len(products)} products to Neo4j...")
    load_to_neo4j(products)
    
    print("\n" + "="*70)
    print("✅ NEO4J DATA LOAD COMPLETED!")
    print("="*70)
    print("\n🌐 Access Neo4j Browser: http://localhost:7474")
    print("   Username: neo4j")
    print("   Password: password123")
    print("\n📝 Try this query:")
    print('   MATCH (p:Product) RETURN p LIMIT 25')
    print()

if __name__ == '__main__':
    main()
