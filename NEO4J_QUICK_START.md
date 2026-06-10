# Neo4j Quick Start - Hướng Dẫn Nhanh

**Ngày**: 9 tháng 6, 2026  
**Trạng thái**: ✅ Đã load 10 products vào Neo4j

---

## ✅ TRẠNG THÁI MÔ HÌNH

### Các Mô Hình Đã Train:

| Mô Hình | File | Kích Thước | Trạng Thái |
|---------|------|------------|-----------|
| **LSTM** | `lstm_model_best.pth` | 947KB | ✅ Trained |
| **Collaborative Filtering** | `cf_model.pkl` | 284KB | ✅ Trained |
| **Random Forest** | `rf_model.pkl` | 2.3MB | ✅ Trained |
| **Ensemble** | `ensemble_weights.pkl` | 94B | ✅ Configured |

**🎉 TẤT CẢ MÔ HÌNH ĐÃ ĐƯỢC TRAIN VÀ SẴN SÀNG SỬ DỤNG!**

---

## 🕸️ NEO4J KNOWLEDGE GRAPH

### 📊 Dữ Liệu Hiện Có:
- ✅ **10 Products** loaded
- ✅ **2 Categories** created
- ✅ **18 SIMILAR_TO relationships** computed
- ✅ **10 IN_CATEGORY relationships** created

---

## 🚀 TRUY CẬP NEO4J

### 1. Web Browser (Dễ nhất)
```
URL: http://localhost:7474
Username: neo4j
Password: password123
```

### 2. Cypher Shell
```bash
docker exec -it neo4j cypher-shell -u neo4j -p password123
```

---

## 🎯 CÁC QUERY CƠ BẢN

### 1. Xem Tất Cả Products
```cypher
MATCH (p:Product)
RETURN p.product_id, p.name, p.category, p.price
LIMIT 10
```

### 2. Xem Products Theo Category
```cypher
MATCH (p:Product)
WHERE p.category = 'Làm đẹp & Sức khỏe'
RETURN p.name, p.price
ORDER BY p.price DESC
```

### 3. Tìm Sản Phẩm Tương Tự
```cypher
// Tìm sản phẩm tương tự với product_id = 52
MATCH (p1:Product {product_id: 52})-[:SIMILAR_TO]->(p2:Product)
RETURN p1.name as gốc, p2.name as tương_tự, p2.price
LIMIT 5
```

### 4. Visualize Graph
```cypher
// Xem toàn bộ graph
MATCH (n)
RETURN n
LIMIT 50
```

### 5. Thống Kê
```cypher
// Đếm nodes và relationships
MATCH (n)
OPTIONAL MATCH (n)-[r]->()
RETURN 
    count(DISTINCT n) as tổng_nodes,
    count(DISTINCT r) as tổng_relationships
```

---

## 🔄 LOAD THÊM DỮ LIỆU

Nếu bạn muốn load lại hoặc load thêm products:

```bash
# Chạy script load data
python3 load_neo4j_data.py

# Hoặc từ container
docker exec ai-service python3 /app/load_neo4j_data.py
```

---

## 🧪 TEST RECOMMENDATION API

### 1. Test Graph-based Recommendations
```bash
curl -s http://localhost:8008/api/v1/recommend \
  -H "Content-Type: application/json" \
  -d '{"user_sequence": [52, 51], "k": 5}' | jq
```

### 2. Test Similar Products
```bash
curl -s http://localhost:8008/api/v1/similar/52?k=5 | jq
```

---

## 📊 KIỂM TRA NHANH

```bash
# Kiểm tra số products trong Neo4j
docker exec neo4j cypher-shell -u neo4j -p password123 \
  "MATCH (n:Product) RETURN count(n) as total"

# Kiểm tra relationships
docker exec neo4j cypher-shell -u neo4j -p password123 \
  "MATCH ()-[r]->() RETURN type(r), count(r)"
```

---

## ❓ TROUBLESHOOTING

### Neo4j trống không có data?
```bash
# Load lại data
python3 load_neo4j_data.py
```

### Muốn xóa toàn bộ và load lại?
```bash
# Xóa tất cả
docker exec neo4j cypher-shell -u neo4j -p password123 \
  "MATCH (n) DETACH DELETE n"

# Load lại
python3 load_neo4j_data.py
```

### Neo4j không kết nối được?
```bash
# Restart Neo4j
docker restart neo4j

# Đợi 30s
sleep 30

# Test connection
docker exec neo4j cypher-shell -u neo4j -p password123 \
  "RETURN 'OK' as status"
```

---

## 📚 TÀI LIỆU CHI TIẾT

- **Hướng dẫn đầy đủ**: `NEO4J_GUIDE.md`
- **Phase 3 README**: `services/ai-service/README_PHASE3.md`
- **Graph module**: `services/ai-service/src/graph.py`

---

## ✅ CHECKLIST

- [x] Neo4j đang chạy
- [x] Đã load 10 products
- [x] Có 2 categories
- [x] Có 18 similarity relationships
- [x] Indexes đã được tạo
- [x] Tất cả models đã train
- [ ] Test API endpoints
- [ ] Truy cập Neo4j Browser để visualize

---

**🎉 HỆ THỐNG ĐÃ SẴN SÀNG!**

Bây giờ bạn có thể:
1. ✅ Truy cập Neo4j Browser để xem graph
2. ✅ Chạy các query Cypher
3. ✅ Test các API recommendations
4. ✅ Tất cả models đã trained và hoạt động

---

**Prepared by**: Kiro AI Assistant  
**Date**: June 9, 2026
