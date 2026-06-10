# AI Service - Quick Start Guide

## 🚀 Khởi động nhanh trong 5 phút

### Yêu cầu
- Docker & Docker Compose đã cài đặt
- 8GB RAM trở lên
- 10GB disk space

---

## Option 1: Standalone Deployment (Khuyến nghị cho testing)

### Bước 1: Di chuyển vào thư mục
```bash
cd services/ai-service
```

### Bước 2: Deploy
```bash
./deploy.sh
```

### Bước 3: Kiểm tra
```bash
# Health check
curl http://localhost:8008/api/v1/health

# API docs
open http://localhost:8008/docs
```

**Xong! Service đã chạy tại http://localhost:8008**

---

## Option 2: Full System Deployment (Production)

### Bước 1: Di chuyển về root directory
```bash
cd /path/to/project
```

### Bước 2: Deploy tất cả services
```bash
docker-compose up -d
```

### Bước 3: Kiểm tra AI Service
```bash
curl http://localhost:8008/api/v1/health
```

**Xong! Toàn bộ hệ thống đã chạy!**

---

## 🧪 Test nhanh

### 1. Health Check
```bash
curl http://localhost:8008/api/v1/health
```

**Expected:**
```json
{
  "status": "healthy",
  "models": {
    "lstm": "loaded",
    "graph": "connected",
    "rag": "ready",
    "hybrid": "ready"
  }
}
```

### 2. Get Statistics
```bash
curl http://localhost:8008/api/v1/stats
```

**Expected:**
```json
{
  "users": 50,
  "products": 50,
  "interactions": 1731,
  "graph_nodes": 160,
  "graph_relationships": 1905
}
```

### 3. Get Recommendations
```bash
curl -X POST http://localhost:8008/api/v1/recommend \
  -H "Content-Type: application/json" \
  -d '{"user_id": 1, "k": 5}'
```

**Expected:**
```json
{
  "recommendations": [
    {
      "product_id": 27,
      "score": 0.375,
      "breakdown": {
        "lstm": 1.0,
        "graph": 0.25,
        "rag": 0.0
      }
    }
  ]
}
```

### 4. Test Chatbot
```bash
curl -X POST http://localhost:8008/api/v1/chatbot \
  -H "Content-Type: application/json" \
  -d '{"query": "Tôi muốn mua laptop"}'
```

**Expected:**
```json
{
  "response": "Dựa trên yêu cầu của bạn...",
  "products": [...]
}
```

---

## 📚 API Endpoints

### Health & Stats
- `GET /api/v1/health` - Health check
- `GET /api/v1/stats` - Statistics

### Recommendations
- `POST /api/v1/recommend` - User-based recommendations
- `POST /api/v1/recommend/query` - Query-based recommendations
- `GET /api/v1/similar/{id}` - Similar products
- `POST /api/v1/smart-recommend` - Smart recommendations (with enrichment)

### Chatbot
- `POST /api/v1/chatbot` - Vietnamese chatbot

### User Context
- `GET /api/v1/user/{id}/context` - User context from microservices

### Documentation
- `GET /docs` - Swagger UI
- `GET /redoc` - ReDoc

---

## 🛠️ Useful Commands

### View Logs
```bash
# AI Service logs
docker logs -f ai-service

# Neo4j logs
docker logs -f neo4j

# All services
docker-compose logs -f
```

### Check Status
```bash
# List running containers
docker ps

# Check resource usage
docker stats ai-service

# Check health
docker inspect ai-service | grep Health -A 10
```

### Restart Service
```bash
# Restart AI Service
docker-compose restart ai-service

# Restart Neo4j
docker-compose restart neo4j

# Restart all
docker-compose restart
```

### Stop Services
```bash
# Stop standalone
docker-compose -f docker-compose.ai.yml down

# Stop full system
docker-compose down

# Stop and remove volumes
docker-compose down -v
```

---

## 🐛 Troubleshooting

### Service không start được?
```bash
# Check logs
docker logs ai-service

# Restart
docker-compose restart ai-service
```

### Neo4j connection refused?
```bash
# Wait for Neo4j to be ready (30-60s)
docker logs neo4j | grep "Started"

# Test connection
docker exec neo4j cypher-shell -u neo4j -p password123 "RETURN 1"
```

### Port đã được sử dụng?
```bash
# Check port 8008
lsof -i :8008

# Kill process
kill -9 <PID>

# Or change port in .env
AI_SERVICE_PORT=8009
```

### Out of memory?
```bash
# Check memory
docker stats

# Increase Docker memory limit
# Docker Desktop > Settings > Resources > Memory > 8GB+
```

---

## 📖 Tài liệu chi tiết

### Phase Documentation
- [Phase 1: Data Preparation](README_PHASE1.md)
- [Phase 2: LSTM Model](README_PHASE2.md)
- [Phase 3: Knowledge Graph](README_PHASE3.md)
- [Phase 4: RAG System](README_PHASE4.md)
- [Phase 5: Hybrid Recommendation](README_PHASE5.md)
- [Phase 6: FastAPI Service](README_PHASE6.md)
- [Phase 7: Microservices Integration](README_PHASE7.md)
- [Phase 8: Deployment](README_PHASE8.md)

### Status & Progress
- [AI Service Status](AI_SERVICE_STATUS.md)
- [Development Progress](AI_SERVICE_PROGRESS.md)

---

## 🎯 Next Steps

### Development
1. Explore API at http://localhost:8008/docs
2. Test different recommendation modes
3. Try the Vietnamese chatbot
4. Check Neo4j browser at http://localhost:7474

### Integration
1. Connect frontend to AI Service
2. Use smart recommendations
3. Implement user context
4. Add product enrichment

### Production
1. Configure environment variables
2. Set up monitoring
3. Configure backups
4. Scale as needed

---

## 💡 Tips

### Performance
- Use `filter_available=true` to filter out-of-stock products
- Adjust weights for different recommendation strategies
- Cache frequently requested recommendations

### Customization
- Modify weights in `/api/v1/recommend/custom-weights`
- Adjust LSTM parameters in environment variables
- Configure RAG model in settings

### Monitoring
- Check `/api/v1/health` regularly
- Monitor `/api/v1/stats` for data insights
- Watch Docker logs for errors

---

## 📞 Support

### Documentation
- Full documentation in README_PHASE*.md files
- API documentation at /docs endpoint
- Status information in AI_SERVICE_STATUS.md

### Testing
- Run phase tests: `python run_phase*.py`
- Run deployment tests: `python run_phase8.py`
- Check all tests: 40/41 passing (97.6%)

---

**🎉 Chúc bạn sử dụng AI Service thành công!**

**Service URL**: http://localhost:8008  
**API Docs**: http://localhost:8008/docs  
**Neo4j Browser**: http://localhost:7474  
**Status**: ✅ Production Ready
