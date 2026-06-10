# Hướng Dẫn Sử Dụng Neo4j Knowledge Graph

**Ngày**: 9 tháng 6, 2026  
**Trạng thái**: Neo4j đang chạy ✅  
**Ports**: 7474 (Browser), 7687 (Bolt)

---

## 🎯 Tổng Quan

Neo4j là **Knowledge Graph Database** được sử dụng để:
- Lưu trữ quan hệ giữa Users, Products, Categories
- Tìm sản phẩm tương tự (similar products)
- Recommend dựa trên graph patterns
- Phân tích user behavior

---

## 🚀 Bước 1: Truy Cập Neo4j Browser

### Cách 1: Web Browser (Dễ nhất)
```bash
# Mở trình duyệt
http://localhost:7474
```

**Đăng nhập**:
- **Username**: `neo4j`
- **Password**: `password123`
- **Connect URL**: `bolt://localhost:7687`

### Cách 2: Command Line
```bash
# Truy cập Cypher Shell
docker exec -it neo4j cypher-shell -u neo4j -p password123
```

---

## 📊 Bước 2: Kiểm Tra Dữ Liệu Hiện Có

### 2.1. Kiểm tra số lượng nodes
```bash
docker exec neo4j cypher-shell -u neo4j -p password123 \
  "MATCH (n) RETURN labels(n) as type, count(n) as count"
```

**Nếu trống** (chưa có dữ liệu), chuyển sang Bước 3.

### 2.2. Kiểm tra relationships
```bash
docker exec neo4j cypher-shell -u neo4j -p password123 \
  "MATCH ()-[r]->() RETURN type(r) as relationship, count(r) as count"
```

---

## 🔄 Bước 3: Load Dữ Liệu Vào Neo4j

### 3.1. Chạy Phase 3 Script (Tự động tạo Graph)

Chúng ta đã có script sẵn:

```bash
# Chạy Phase 3 - Tạo Knowledge Graph
docker exec ai-service python3 run_phase3.py
```

**Script này sẽ**:
1. ✅ Kết nối với Product Service để lấy danh sách products
2. ✅ Tạo Product nodes trong Neo4j
3. ✅ Tạo Category nodes
4. ✅ Tạo relationships: Product → Category
5. ✅ Tính toán product similarity
6. ✅ Tạo SIMILAR_TO relationships

**Thời gian**: ~30 giây

### 3.2. Kiểm tra kết quả
```bash
# Xem số nodes đã tạo
docker exec neo4j cypher-shell -u neo4j -p password123 \
  "MATCH (n) RETURN labels(n) as type, count(n) as count"

# Expected output:
# ["Product"]  100
# ["Category"] 10
```

---

## 🎨 Bước 4: Truy Vấn Cơ Bản (Cypher Queries)

### 4.1. Xem tất cả Products
```cypher
MATCH (p:Product)
RETURN p.product_id, p.name, p.category, p.price
LIMIT 10
```

### 4.2. Xem Products theo Category
```cypher
MATCH (p:Product)
WHERE p.category = 'Điện thoại & Tablet'
RETURN p.name, p.price
ORDER BY p.price DESC
LIMIT 5
```

### 4.3. Tìm sản phẩm tương tự
```cypher
// Tìm sản phẩm tương tự với product_id = 1
MATCH (p1:Product {product_id: 1})-[:SIMILAR_TO]->(p2:Product)
RETURN p1.name as original, p2.name as similar, p2.price
LIMIT 5
```

### 4.4. Sản phẩm phổ biến nhất trong category
```cypher
MATCH (p:Product)
WHERE p.category = 'Laptop & Máy tính'
RETURN p.name, p.price, p.stock
ORDER BY p.stock DESC
LIMIT 5
```

### 4.5. Phân tích Category
```cypher
MATCH (p:Product)
RETURN p.category as category, 
       count(p) as total_products,
       avg(p.price) as avg_price,
       sum(p.stock) as total_stock
ORDER BY total_products DESC
```

---

## 🧪 Bước 5: Test Recommendation API

### 5.1. Test Graph Recommendations
```bash
# Gợi ý dựa trên Knowledge Graph
curl -s http://localhost:8008/api/v1/recommend \
  -H "Content-Type: application/json" \
  -d '{"user_sequence": [1, 2, 3], "k": 5}' | jq
```

### 5.2. Test Similar Products
```bash
# Tìm sản phẩm tương tự với product_id = 5
curl -s http://localhost:8008/api/v1/similar/5?k=5 | jq
```

---

## 📈 Bước 6: Nâng Cao - Thêm User Behavior

### 6.1. Thêm User Nodes
```cypher
// Tạo một user mẫu
CREATE (u:User {
    user_id: 1,
    username: 'john_doe',
    email: 'john@example.com'
})
RETURN u
```

### 6.2. Thêm User-Product Relationships
```cypher
// User mua product
MATCH (u:User {user_id: 1})
MATCH (p:Product {product_id: 10})
CREATE (u)-[:PURCHASED {
    timestamp: datetime(),
    quantity: 1
}]->(p)
RETURN u, p
```

### 6.3. Thêm View Behavior
```cypher
// User xem product
MATCH (u:User {user_id: 1})
MATCH (p:Product {product_id: 15})
MERGE (u)-[v:VIEWED]->(p)
ON CREATE SET v.count = 1, v.first_at = datetime()
ON MATCH SET v.count = v.count + 1, v.last_at = datetime()
RETURN u, p, v
```

### 6.4. Recommend dựa trên User History
```cypher
// Gợi ý cho user dựa trên lịch sử mua
MATCH (u:User {user_id: 1})-[:PURCHASED]->(p1:Product)
MATCH (p1)-[:SIMILAR_TO]->(rec:Product)
WHERE NOT (u)-[:PURCHASED]->(rec)
RETURN rec.name, rec.price, count(*) as score
ORDER BY score DESC
LIMIT 5
```

---

## 🔍 Bước 7: Visualize Graph

### 7.1. Trong Neo4j Browser
```cypher
// Xem toàn bộ graph (giới hạn 50 nodes)
MATCH (n)
RETURN n
LIMIT 50
```

### 7.2. Xem Category Network
```cypher
// Visualize products và categories
MATCH (p:Product)-[:IN_CATEGORY]->(c:Category)
RETURN p, c
LIMIT 100
```

### 7.3. Xem Similarity Network
```cypher
// Visualize product similarities
MATCH (p1:Product)-[s:SIMILAR_TO]->(p2:Product)
RETURN p1, s, p2
LIMIT 50
```

---

## 🛠️ Bước 8: Troubleshooting

### Vấn đề 1: Neo4j không có dữ liệu
```bash
# Chạy lại Phase 3
docker exec ai-service python3 run_phase3.py

# Hoặc chạy từng bước
docker exec -it ai-service python3

>>> from src.graph import ProductKnowledgeGraph
>>> graph = ProductKnowledgeGraph(
...     uri="bolt://neo4j:7687",
...     user="neo4j",
...     password="password123"
... )
>>> # Import products từ Product Service
>>> # (code in run_phase3.py)
```

### Vấn đề 2: Không kết nối được Neo4j
```bash
# Kiểm tra Neo4j logs
docker logs neo4j --tail 50

# Restart Neo4j
docker restart neo4j

# Đợi 30s để Neo4j khởi động
sleep 30

# Test connection
docker exec neo4j cypher-shell -u neo4j -p password123 "RETURN 'OK' as status"
```

### Vấn đề 3: Xóa toàn bộ dữ liệu (Reset)
```bash
# ⚠️ CẢNH BÁO: Xóa TẤT CẢ dữ liệu trong Neo4j
docker exec neo4j cypher-shell -u neo4j -p password123 \
  "MATCH (n) DETACH DELETE n"

# Sau đó chạy lại Phase 3
docker exec ai-service python3 run_phase3.py
```

---

## 📊 Bước 9: Kiểm Tra Graph Statistics

### 9.1. Thống kê tổng quan
```cypher
// Số lượng nodes và relationships
MATCH (n)
OPTIONAL MATCH (n)-[r]->()
RETURN 
    count(DISTINCT n) as total_nodes,
    count(DISTINCT r) as total_relationships
```

### 9.2. Top products có nhiều similarity nhất
```cypher
MATCH (p:Product)-[:SIMILAR_TO]->(similar)
RETURN p.name, count(similar) as similarity_count
ORDER BY similarity_count DESC
LIMIT 10
```

### 9.3. Average product similarity score
```cypher
MATCH ()-[s:SIMILAR_TO]->()
RETURN 
    avg(s.score) as avg_similarity,
    max(s.score) as max_similarity,
    min(s.score) as min_similarity
```

---

## 🎓 Bước 10: Best Practices

### 10.1. Indexing (Tăng tốc query)
```cypher
// Tạo index cho product_id
CREATE INDEX product_id_index IF NOT EXISTS
FOR (p:Product) ON (p.product_id)

// Tạo index cho category
CREATE INDEX category_index IF NOT EXISTS
FOR (p:Product) ON (p.category)

// Xem các indexes
SHOW INDEXES
```

### 10.2. Constraints (Đảm bảo unique)
```cypher
// Product ID phải unique
CREATE CONSTRAINT product_id_unique IF NOT EXISTS
FOR (p:Product) REQUIRE p.product_id IS UNIQUE

// User ID phải unique
CREATE CONSTRAINT user_id_unique IF NOT EXISTS
FOR (u:User) REQUIRE u.user_id IS UNIQUE
```

---

## 🚀 Script Tự Động Hóa

Tạo file `neo4j_setup.sh`:

```bash
#!/bin/bash

echo "🕸️  NEO4J KNOWLEDGE GRAPH SETUP"
echo "================================"

# 1. Check Neo4j is running
echo "1. Checking Neo4j status..."
if docker ps | grep -q neo4j; then
    echo "   ✅ Neo4j is running"
else
    echo "   ❌ Neo4j is not running"
    echo "   Starting Neo4j..."
    docker start neo4j
    sleep 30
fi

# 2. Clear existing data (optional)
read -p "2. Clear existing data? (y/N): " clear_data
if [ "$clear_data" = "y" ]; then
    echo "   Clearing Neo4j data..."
    docker exec neo4j cypher-shell -u neo4j -p password123 \
        "MATCH (n) DETACH DELETE n" 2>/dev/null
    echo "   ✅ Data cleared"
fi

# 3. Run Phase 3 - Load data
echo "3. Loading products into Neo4j..."
docker exec ai-service python3 run_phase3.py

# 4. Create indexes
echo "4. Creating indexes..."
docker exec neo4j cypher-shell -u neo4j -p password123 \
    "CREATE INDEX product_id_index IF NOT EXISTS FOR (p:Product) ON (p.product_id)" 2>/dev/null

docker exec neo4j cypher-shell -u neo4j -p password123 \
    "CREATE INDEX category_index IF NOT EXISTS FOR (p:Product) ON (p.category)" 2>/dev/null

# 5. Show statistics
echo ""
echo "📊 NEO4J STATISTICS"
echo "================================"
docker exec neo4j cypher-shell -u neo4j -p password123 \
    "MATCH (n) RETURN labels(n) as type, count(n) as count"

echo ""
echo "✅ Setup complete!"
echo ""
echo "🌐 Access Neo4j Browser:"
echo "   http://localhost:7474"
echo "   Username: neo4j"
echo "   Password: password123"
```

**Sử dụng**:
```bash
chmod +x neo4j_setup.sh
./neo4j_setup.sh
```

---

## 📚 Resources

### Neo4j Documentation
- Browser: http://localhost:7474
- Cypher Manual: https://neo4j.com/docs/cypher-manual/current/
- Graph Data Science: https://neo4j.com/docs/graph-data-science/

### Trong Project
- Graph module: `services/ai-service/src/graph.py`
- Phase 3 script: `services/ai-service/run_phase3.py`
- README Phase 3: `services/ai-service/README_PHASE3.md`

---

## ✅ Checklist

- [ ] Neo4j đang chạy (port 7474, 7687)
- [ ] Truy cập được Neo4j Browser
- [ ] Chạy `run_phase3.py` để load data
- [ ] Kiểm tra có products trong Neo4j
- [ ] Test query cơ bản
- [ ] Test API recommendations
- [ ] Tạo indexes
- [ ] (Optional) Thêm user behavior data

---

**Prepared by**: Kiro AI Assistant  
**Date**: June 9, 2026  
**Status**: Production Ready ✅
