# Giai đoạn 6: Dịch vụ FastAPI - HOÀN THÀNH ✅

## Tổng quan
Giai đoạn 6 đóng gói hệ thống AI thành REST API sử dụng FastAPI, cung cấp các endpoints để tích hợp với các microservices khác trong hệ thống e-commerce.

## Kiến trúc

### Cấu trúc dự án
```
services/ai-service/
├── main.py                    # FastAPI application
├── models/
│   ├── __init__.py
│   └── schemas.py            # Pydantic models
├── routers/
│   ├── __init__.py
│   ├── health.py             # Health check endpoints
│   ├── recommend.py          # Recommendation endpoints
│   └── chatbot.py            # Chatbot endpoints
├── services/
│   ├── __init__.py
│   └── ai_manager.py         # AI models manager
└── src/                      # AI components (Phase 1-5)
```

### Các thành phần

#### 1. FastAPI Application (main.py)
- Lifespan management (startup/shutdown)
- CORS middleware
- Router integration
- Global AI Manager

#### 2. AI Manager (services/ai_manager.py)
- Quản lý tất cả các mô hình AI
- Khởi tạo LSTM, Graph, RAG, Hybrid
- Cung cấp interface thống nhất
- Health monitoring

#### 3. Pydantic Schemas (models/schemas.py)
- Request validation
- Response formatting
- Type safety
- API documentation

#### 4. Routers
- **health.py**: Health check và statistics
- **recommend.py**: Gợi ý sản phẩm
- **chatbot.py**: Chatbot tư vấn

## API Endpoints

### Base URL
```
http://localhost:8000
```

### 1. Health Check

#### GET /api/v1/health
Kiểm tra sức khỏe của dịch vụ

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "components": {
    "lstm": "healthy",
    "graph": "healthy",
    "rag": "healthy",
    "hybrid": "healthy"
  }
}
```

### 2. Statistics

#### GET /api/v1/stats
Lấy thống kê về hệ thống AI

**Response:**
```json
{
  "total_products": 50,
  "total_users": 100,
  "total_interactions": 1731,
  "model_info": {
    "lstm": {
      "parameters": 241267,
      "vocab_size": 51,
      "embedding_dim": 64,
      "hidden_dim": 128
    },
    "graph": {
      "nodes": {...},
      "relationships": {...}
    },
    "rag": {
      "vectors": 50,
      "embedding_dim": 384,
      "model": "paraphrase-multilingual-MiniLM-L12-v2"
    }
  }
}
```

### 3. Recommendations

#### POST /api/v1/recommend
Lấy gợi ý sản phẩm (hybrid)

**Request Body:**
```json
{
  "user_id": 1,
  "user_sequence": [1, 2, 3, 4, 5],
  "query": "laptop gaming",
  "product_id": 10,
  "k": 10,
  "exclude_seen": true,
  "weights": {
    "lstm": 0.3,
    "graph": 0.3,
    "rag": 0.4
  }
}
```

**Các tham số** (tất cả đều optional, nhưng phải có ít nhất 1):
- `user_id`: ID người dùng
- `user_sequence`: Chuỗi sản phẩm đã xem
- `query`: Truy vấn văn bản
- `product_id`: ID sản phẩm để tìm tương tự
- `k`: Số lượng gợi ý (1-50, mặc định: 10)
- `exclude_seen`: Loại trừ sản phẩm đã xem
- `weights`: Trọng số tùy chỉnh

**Response:**
```json
{
  "recommendations": [
    {
      "product_id": 27,
      "score": 0.3750,
      "breakdown": {
        "final_score": 0.3750,
        "lstm": 1.0000,
        "graph": 0.2500,
        "rag": 0.0000
      }
    }
  ],
  "total": 10,
  "recommendation_type": "hybrid",
  "weights_used": {
    "lstm": 0.3,
    "graph": 0.3,
    "rag": 0.4
  }
}
```

#### GET /api/v1/similar/{product_id}
Tìm sản phẩm tương tự

**Parameters:**
- `product_id`: ID sản phẩm (path parameter)
- `k`: Số lượng gợi ý (query parameter, mặc định: 10)

**Example:**
```
GET /api/v1/similar/1?k=5
```

**Response:** Giống `/recommend`

### 4. Chatbot

#### POST /api/v1/chatbot
Tương tác với chatbot

**Request Body:**
```json
{
  "message": "Tôi muốn mua laptop gaming",
  "user_id": 1,
  "conversation_id": "conv_abc123"
}
```

**Response:**
```json
{
  "response": "Tôi tìm thấy 5 sản phẩm phù hợp:\n\n1. 📦 ASUS ROG Strix G16...",
  "products": null,
  "conversation_id": "conv_abc123"
}
```

## Cách chạy

### 1. Cài đặt dependencies
```bash
cd services/ai-service
source venv/bin/activate
pip install fastapi uvicorn[standard] pydantic httpx python-multipart requests
```

### 2. Khởi động Neo4j
```bash
docker compose -f docker-compose.neo4j.yml up -d
```

### 3. Khởi động FastAPI service
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### 4. Truy cập API Documentation
```
http://localhost:8000/docs
```

### 5. Chạy tests
```bash
python run_phase6.py
```

## Kết quả kiểm thử

### Test Results: 7/7 PASS (100%)

✅ **Test 1: Health Check**
- Status: healthy
- All components: healthy

✅ **Test 2: Statistics**
- 50 products, 100 users, 1,731 interactions
- Model info complete

✅ **Test 3: User-based Recommendation**
- Input: user_id=1, sequence=[1,2,3,4,5]
- Output: Top-5 products with scores

✅ **Test 4: Query-based Recommendation**
- Input: "laptop gaming mạnh mẽ"
- Output: ASUS ROG (0.40), Dell XPS (0.29)

✅ **Test 5: Similar Products**
- Input: product_id=1
- Output: iPad (0.60), Xiaomi (0.59), Samsung (0.55)

✅ **Test 6: Chatbot**
- Greeting: "Xin chào" → Welcome message
- Search: "laptop gaming" → Product list
- Query: "iPhone" → iPhone products

✅ **Test 7: Hybrid with Custom Weights**
- Custom weights: LSTM=0.2, Graph=0.2, RAG=0.6
- Successfully applied

## Ví dụ sử dụng

### Python Client
```python
import requests

BASE_URL = "http://localhost:8000"

# 1. Health check
response = requests.get(f"{BASE_URL}/api/v1/health")
print(response.json())

# 2. Get recommendations
payload = {
    "user_sequence": [1, 2, 3],
    "query": "laptop gaming",
    "k": 10
}
response = requests.post(f"{BASE_URL}/api/v1/recommend", json=payload)
recommendations = response.json()

# 3. Chatbot
payload = {
    "message": "Tôi muốn mua điện thoại"
}
response = requests.post(f"{BASE_URL}/api/v1/chatbot", json=payload)
print(response.json()['response'])

# 4. Similar products
response = requests.get(f"{BASE_URL}/api/v1/similar/1?k=5")
similar = response.json()
```

### cURL Examples
```bash
# Health check
curl http://localhost:8000/api/v1/health

# Recommendations
curl -X POST http://localhost:8000/api/v1/recommend \
  -H "Content-Type: application/json" \
  -d '{
    "query": "laptop gaming",
    "k": 5
  }'

# Similar products
curl http://localhost:8000/api/v1/similar/1?k=5

# Chatbot
curl -X POST http://localhost:8000/api/v1/chatbot \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Tôi muốn mua laptop"
  }'
```

### JavaScript/Fetch
```javascript
// Recommendations
const response = await fetch('http://localhost:8000/api/v1/recommend', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    query: 'laptop gaming',
    k: 10
  })
});

const data = await response.json();
console.log(data.recommendations);
```

## Hiệu suất

### Thời gian khởi động
- **LSTM**: ~1 giây
- **Graph**: ~2 giây
- **RAG**: ~3 giây
- **Tổng**: ~6 giây

### Thời gian phản hồi
- **Health check**: <10ms
- **Statistics**: <50ms
- **Recommendations**: 100-200ms
- **Chatbot**: 50-150ms
- **Similar products**: 100-150ms

### Tài nguyên
- **RAM**: ~2GB
- **CPU**: 10-20% (idle), 50-80% (active)
- **Disk**: ~3GB

## Tính năng

### ✅ Đã triển khai
1. **Health Monitoring**
   - Component status
   - Version info
   - Statistics

2. **Hybrid Recommendations**
   - User-based
   - Query-based
   - Product-based
   - Custom weights

3. **Chatbot**
   - Vietnamese support
   - Product search
   - Conversational

4. **API Documentation**
   - Swagger UI
   - ReDoc
   - OpenAPI schema

5. **Error Handling**
   - Validation errors
   - Runtime errors
   - Graceful degradation

6. **CORS Support**
   - Cross-origin requests
   - Configurable origins

### 🔜 Cải tiến tương lai
1. **Authentication**
   - API keys
   - JWT tokens
   - Rate limiting

2. **Caching**
   - Redis integration
   - Response caching
   - Model caching

3. **Monitoring**
   - Prometheus metrics
   - Logging
   - Tracing

4. **Performance**
   - Async processing
   - Batch requests
   - Connection pooling

## Error Handling

### Validation Errors (400)
```json
{
  "detail": [
    {
      "loc": ["body", "k"],
      "msg": "ensure this value is less than or equal to 50",
      "type": "value_error"
    }
  ]
}
```

### Runtime Errors (500)
```json
{
  "detail": "Lỗi khi tạo gợi ý: Connection refused"
}
```

### Component Errors
- LSTM unavailable → Use Graph + RAG
- Graph unavailable → Use LSTM + RAG
- RAG unavailable → Use LSTM + Graph

## Deployment

### Docker (Phase 8)
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Docker Compose
```yaml
ai-service:
  build: ./services/ai-service
  ports:
    - "8008:8000"
  environment:
    - NEO4J_URI=bolt://neo4j:7687
  depends_on:
    - neo4j
```

## Bảo mật

### Khuyến nghị
1. **CORS**: Chỉ định origins cụ thể trong production
2. **Rate Limiting**: Giới hạn requests per IP
3. **Authentication**: Thêm API key hoặc JWT
4. **Input Validation**: Đã có với Pydantic
5. **HTTPS**: Sử dụng trong production

## Troubleshooting

### Service không khởi động
```bash
# Kiểm tra logs
tail -f logs/ai-service.log

# Kiểm tra Neo4j
docker ps | grep neo4j

# Kiểm tra port
lsof -i :8000
```

### Recommendations chậm
- Kiểm tra Neo4j connection
- Tăng timeout
- Sử dụng caching

### Memory issues
- Giảm batch size
- Unload unused models
- Increase RAM

## Bước tiếp theo

Giai đoạn 6 đã hoàn thành! FastAPI service đã sẵn sàng cho:
- **Giai đoạn 7**: Tích hợp với microservices (Order, Product, User services)
- **Giai đoạn 8**: Deployment (Docker, docker-compose, production)

---

**Trạng thái**: ✅ Hoàn thành và đã kiểm tra  
**Tests**: 7/7 PASS (100%)  
**API Docs**: http://localhost:8000/docs  
**Sẵn sàng cho**: Giai đoạn 7 - Tích hợp microservices
