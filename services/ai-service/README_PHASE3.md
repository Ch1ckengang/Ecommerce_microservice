# Giai đoạn 3: Knowledge Graph (Neo4j) ✅

## Tổng quan
Giai đoạn 3 triển khai Knowledge Graph sử dụng Neo4j để mô hình hóa mối quan hệ giữa người dùng và sản phẩm, cho phép gợi ý dựa trên đồ thị.

## Các nhiệm vụ đã hoàn thành

### ✅ Nhiệm vụ 3.1: Cài đặt Neo4j
- **File**: `docker-compose.neo4j.yml`
- **Container**: neo4j:5.15.0
- **Cổng**:
  - HTTP: 7474
  - Bolt: 7687
- **Thông tin đăng nhập**:
  - Username: neo4j
  - Password: password123

### ✅ Nhiệm vụ 3.2: Tạo schema đồ thị
- **File**: `src/graph.py`
- **Nodes**:
  - `User`: Đại diện người dùng (100 nodes)
  - `Product`: Đại diện sản phẩm (50 nodes)
  - `Category`: Danh mục sản phẩm (10 nodes)

- **Relationships**:
  - `(User)-[:VIEWED]->(Product)`: 785 mối quan hệ
  - `(User)-[:ADDED_TO_CART]->(Product)`: 482 mối quan hệ
  - `(User)-[:PURCHASED]->(Product)`: 188 mối quan hệ
  - `(Product)-[:SIMILAR_TO]->(Product)`: 400 mối quan hệ
  - `(Product)-[:IN_CATEGORY]->(Category)`: 50 mối quan hệ

### ✅ Nhiệm vụ 3.3: Chèn dữ liệu mẫu
- Đã tải 1,455 tương tác người dùng từ `user_behavior.csv`
- Đã tạo 100 user nodes
- Đã tạo 50 product nodes
- Đã tạo 10 category nodes
- Đã tạo 400 mối quan hệ tương đồng dựa trên đồng xuất hiện

### ✅ Nhiệm vụ 3.4: Truy vấn gợi ý
Đã triển khai 3 loại gợi ý dựa trên đồ thị:

1. **Gợi ý dựa trên người dùng**
   - Tìm sản phẩm tương tự dựa trên lịch sử người dùng
   - Sử dụng lọc cộng tác thông qua duyệt đồ thị

2. **Gợi ý dựa trên danh mục**
   - Gợi ý sản phẩm từ cùng danh mục
   - Xếp hạng theo độ phổ biến (số lượt mua)

3. **Gợi ý dựa trên độ tương đồng**
   - Gợi ý sản phẩm tương tự
   - Dựa trên mẫu đồng xuất hiện

## Thống kê đồ thị

```
📊 Thống kê đồ thị:
==================================================
Nodes:
   Users: 100
   Products: 50
   Categories: 10
   Tổng: 160

Relationships:
   VIEWED: 785
   ADDED_TO_CART: 482
   PURCHASED: 188
   SIMILAR_TO: 400
   IN_CATEGORY: 50
   TỔNG: 1,905
==================================================
```

## Các file được tạo

```
docker-compose.neo4j.yml    # Cấu hình Neo4j Docker
src/graph.py                # Triển khai knowledge graph
run_phase3.py               # Script thực thi Giai đoạn 3
```

## Cách chạy

### Yêu cầu
```bash
cd services/ai-service
source venv/bin/activate
pip install neo4j==5.15.0
```

### Khởi động Neo4j
```bash
docker compose -f docker-compose.neo4j.yml up -d
```

### Xây dựng Knowledge Graph
```bash
python run_phase3.py
```

### Kết quả mong đợi
```
📌 GIAI ĐOẠN 3 — KNOWLEDGE GRAPH (Neo4j)
==================================================

🐳 Đang khởi động Neo4j Docker Container
✅ Container Neo4j đã khởi động
   HTTP: http://localhost:7474
   Bolt: bolt://localhost:7687

🏗️  Đang xây dựng Knowledge Graph
✅ Đã kết nối với Neo4j
✅ Đã xóa database
✅ Đã tạo constraints
✅ Đã tạo indexes

📂 Đang tải hành vi người dùng...
   Đã tải 1455 tương tác

👥 Đang tạo User nodes...
   Đã tạo 100 users

📦 Đang tạo Product nodes...
   Đã tạo 50 products

🔗 Đang tạo relationships...
   Đã tạo 785 VIEWED relationships
   Đã tạo 482 ADDED_TO_CART relationships
   Đã tạo 188 PURCHASED relationships

📁 Đang tạo danh mục sản phẩm...
   Đã tạo 10 categories
   Đã liên kết products với categories

🔗 Đang tạo product similarity relationships...
   Đã tạo 400 similarity relationships

📊 Thống kê đồ thị:
   [Thống kê được hiển thị]

✅ GIAI ĐOẠN 3 HOÀN THÀNH!
```

## Ví dụ gợi ý

### 1. Gợi ý dựa trên người dùng
```python
from graph import ProductKnowledgeGraph

graph = ProductKnowledgeGraph()
recommendations = graph.recommend_by_user_history(user_id=1, k=5)

# Đầu ra:
# [(19, 5.0), (36, 5.0), (45, 4.0), (44, 4.0), (42, 4.0)]
```

**Giải thích**: User 1 nhận gợi ý dựa trên sản phẩm mà những người dùng tương tự đã tương tác.

### 2. Gợi ý dựa trên danh mục
```python
recommendations = graph.recommend_by_category(product_id=1, k=5)

# Đầu ra:
# [(2, 8.0), (4, 5.0), (3, 4.0), (5, 4.0)]
```

**Giải thích**: Sản phẩm 1 (iPhone) gợi ý các sản phẩm khác từ danh mục "Điện thoại & Tablet", xếp hạng theo độ phổ biến.

### 3. Gợi ý dựa trên độ tương đồng
```python
recommendations = graph.recommend_similar_products(product_id=1, k=5)

# Đầu ra:
# [(2, 8.0), (3, 8.0), (4, 8.0), (5, 7.0), (44, 5.0)]
```

**Giải thích**: Các sản phẩm thường được xem cùng với Sản phẩm 1.

## Truy vấn đồ thị (Cypher)

### Xem tất cả relationships cho một user
```cypher
MATCH (u:User {user_id: 1})-[r]->(p:Product)
RETURN u, r, p
```

### Tìm sản phẩm tương tự
```cypher
MATCH (p1:Product {product_id: 1})-[:SIMILAR_TO]->(p2:Product)
RETURN p1, p2
ORDER BY p2.product_id
```

### Tìm sản phẩm trong một danh mục
```cypher
MATCH (p:Product)-[:IN_CATEGORY]->(c:Category {name: 'Điện thoại & Tablet'})
RETURN p.product_id, p.category
```

### Tìm người dùng đã mua một sản phẩm
```cypher
MATCH (u:User)-[:PURCHASED]->(p:Product {product_id: 1})
RETURN u.user_id
```

## Neo4j Browser

Truy cập Neo4j Browser tại: http://localhost:7474

**Đăng nhập**:
- Username: `neo4j`
- Password: `password123`

**Truy vấn hữu ích**:
```cypher
// Xem schema đồ thị
CALL db.schema.visualization()

// Đếm tất cả nodes
MATCH (n) RETURN labels(n), COUNT(n)

// Đếm tất cả relationships
MATCH ()-[r]->() RETURN type(r), COUNT(r)

// Xem dữ liệu mẫu
MATCH (u:User)-[r]->(p:Product)
RETURN u, r, p
LIMIT 25
```

## Tích hợp với Python

```python
from graph import ProductKnowledgeGraph

# Khởi tạo
graph = ProductKnowledgeGraph(
    uri="bolt://localhost:7687",
    user="neo4j",
    password="password123"
)

# Lấy gợi ý
user_recs = graph.recommend_by_user_history(user_id=1, k=10)
category_recs = graph.recommend_by_category(product_id=5, k=10)
similar_recs = graph.recommend_similar_products(product_id=5, k=10)

# Lấy thống kê
stats = graph.get_statistics()
print(stats)

# Đóng kết nối
graph.close()
```

## Hiệu suất

- **Thời gian xây dựng đồ thị**: ~5 giây
- **Thời gian truy vấn**: <100ms mỗi truy vấn gợi ý
- **Sử dụng bộ nhớ**: ~512MB (đã cấu hình)
- **Lưu trữ**: ~50MB cho dữ liệu đồ thị

## Ưu điểm của Knowledge Graph

1. **Dựa trên mối quan hệ**: Nắm bắt các mối quan hệ phức tạp giữa các thực thể
2. **Có thể giải thích**: Có thể truy vết tại sao một gợi ý được đưa ra
3. **Linh hoạt**: Dễ dàng thêm các loại mối quan hệ mới
4. **Thời gian thực**: Truy vấn duyệt đồ thị nhanh
5. **Lọc cộng tác**: Tận dụng các mẫu hành vi người dùng

## Bước tiếp theo

Giai đoạn 3 đã hoàn thành! Knowledge Graph đã sẵn sàng cho:
- **Giai đoạn 4**: Hệ thống RAG (Vector search + LLM)
- **Giai đoạn 5**: Gợi ý kết hợp (LSTM + Graph + RAG)
- **Giai đoạn 6**: Tích hợp dịch vụ FastAPI

## Khắc phục sự cố

### Neo4j không khởi động
```bash
# Kiểm tra logs
docker logs neo4j-graph

# Khởi động lại container
docker compose -f docker-compose.neo4j.yml restart
```

### Kết nối bị từ chối
```bash
# Đợi Neo4j sẵn sàng (mất ~15 giây)
sleep 15

# Kiểm tra kết nối
docker exec neo4j-graph cypher-shell -u neo4j -p password123 "RETURN 1"
```

### Xóa và xây dựng lại đồ thị
```python
from graph import build_knowledge_graph

graph = build_knowledge_graph(clear_existing=True)
```

---

**Trạng thái**: ✅ Hoàn thành và đã kiểm tra
**Phiên bản Neo4j**: 5.15.0
**Sẵn sàng cho**: Giai đoạn 4 - Hệ thống RAG
