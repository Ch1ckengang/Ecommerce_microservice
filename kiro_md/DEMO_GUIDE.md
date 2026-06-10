# 🎬 HƯỚNG DẪN DEMO - E-COMMERCE MICROSERVICES

**Thời gian demo:** 15-20 phút  
**Chuẩn bị:** 10 phút

---

## 📋 CHECKLIST TRƯỚC KHI DEMO

### 1. Kiểm tra hệ thống (5 phút)
```bash
# Check Docker
docker --version
docker compose version

# Check disk space (cần ít nhất 10GB)
df -h

# Check memory (cần ít nhất 8GB)
free -h
```

### 2. Khởi động services (3 phút)
```bash
# Start all services
cd /home/trung/Documents/TieuluanS.A&D
docker-compose up -d

# Wait for all services to be healthy
sleep 120

# Check status
docker-compose ps
```

### 3. Chạy demo setup (2 phút)
```bash
# Create demo data
./demo_setup.sh

# Verify
./test_full_flow.sh
```

---

## 🎯 DEMO SCRIPT (15-20 phút)

### Part 1: Giới thiệu kiến trúc (3 phút)

**Mở slide/diagram:**
```
"Hệ thống gồm 7 microservices độc lập:
- User Service: Quản lý người dùng
- Product Service: Quản lý sản phẩm với 3 domain (Book/Electronics/Fashion)
- Cart Service: Giỏ hàng
- Order Service: Đơn hàng
- Payment Service: Thanh toán
- Shipping Service: Vận chuyển
- AI Service: Gợi ý sản phẩm (LSTM + Graph + RAG)

Tất cả qua API Gateway (Nginx) và sử dụng JWT authentication.
8 databases: 3 MySQL + 4 PostgreSQL + 1 Neo4j"
```

**Mở terminal:**
```bash
# Show running containers
docker-compose ps

# Show architecture
cat docker-compose.yml | head -50
```

---

### Part 2: User Flow - Đăng ký & Đăng nhập (3 phút)

**Mở browser: http://localhost:8007**

1. **Trang chủ**
   - "Đây là frontend service, port 8007"
   - "Tích hợp với tất cả backend services"

2. **Đăng ký (Register)**
   ```
   Username: demo_user_1
   Email: demo1@example.com
   Password: Demo@123456
   ```
   - Click "Đăng ký"
   - "User Service (MySQL) tạo account"

3. **Đăng nhập (Login)**
   ```
   Username: demo_user_1
   Password: Demo@123456
   ```
   - "JWT token được tạo và lưu trong session"
   - Giải thích: "Access token 60 phút, refresh token 7 ngày"

4. **Xem Profile**
   - Click "Profile" trên navbar
   - "Hiển thị thông tin user từ User Service"

---

### Part 3: Product Browsing (3 phút)

**Vẫn trên browser:**

1. **Danh sách sản phẩm**
   - Click "Products" hoặc navigate to http://localhost:8007/products/
   - "Product Service (PostgreSQL) trả về danh sách"
   - "Có 10+ sản phẩm demo"

2. **Chi tiết sản phẩm**
   - Click vào 1 sản phẩm bất kỳ
   - "Hiển thị thông tin chi tiết"
   - **Point out:** "Sản phẩm tương tự" ở dưới (AI recommendations)
   - "AI Service dùng hybrid model để gợi ý"

3. **Kiểm tra domain models (Optional)**
   - Mở terminal mới:
   ```bash
   # Check Book details
   curl http://localhost:8001/api/products/1/book/
   
   # Check Electronics details
   curl http://localhost:8001/api/products/6/electronics/
   
   # Check Fashion details
   curl http://localhost:8001/api/products/11/fashion/
   ```

---

### Part 4: Shopping Flow - Mua hàng (5 phút)

**Tiếp tục trên browser:**

1. **Thêm vào giỏ hàng**
   - Ở trang product detail, nhập số lượng
   - Click "Thêm vào giỏ hàng"
   - "Cart Service (MySQL) tạo cart và cart item"

2. **Xem giỏ hàng**
   - Click "Cart" trên navbar hoặc navigate to /cart/
   - "Hiển thị sản phẩm đã thêm với giá và tổng tiền"
   - **Thêm 1-2 sản phẩm nữa** (optional)

3. **Checkout - Tạo đơn hàng**
   - Click "Thanh toán" / "Checkout"
   - Điền shipping address:
     ```
     Địa chỉ: 123 Nguyễn Huệ, Quận 1, TP.HCM
     Số điện thoại: 0901234567
     ```
   - Click "Đặt hàng"
   
   **Giải thích quá trình:**
   ```
   "Khi click đặt hàng, hệ thống thực hiện:
   1. Order Service kiểm tra stock với Product Service
   2. Nếu đủ hàng, tạo order và trừ stock
   3. Tự động tạo payment (Payment Service)
   4. Tự động tạo shipment (Shipping Service)
   5. Xóa giỏ hàng (Cart Service)
   
   Tất cả trong 1 transaction flow."
   ```

4. **Xem đơn hàng**
   - Click "Orders" trên navbar
   - Click vào order vừa tạo
   - "Hiển thị chi tiết: items, payment status, shipping status"

---

### Part 5: AI Service Demo (3-4 phút)

**Option A: Qua UI (Frontend)**

1. **AI Chatbot**
   - Navigate to http://localhost:8007/chatbot/
   - Test queries:
     ```
     "Tôi muốn mua laptop"
     "Giới thiệu sách hay"
     "Tìm điện thoại giá rẻ"
     ```
   - "RAG system tìm kiếm sản phẩm phù hợp bằng semantic search"

2. **AI Recommendations**
   - Ở product detail page, xem "Sản phẩm tương tự"
   - "Hybrid recommendation: LSTM + Graph + RAG"

**Option B: Qua API (Terminal)**

```bash
# Health check
curl http://localhost:8008/api/v1/health

# Get recommendations for user
curl -X POST http://localhost:8008/api/v1/recommend \
  -H "Content-Type: application/json" \
  -d '{"user_id": 1, "k": 5}'

# Chatbot
curl -X POST http://localhost:8008/api/v1/chatbot \
  -H "Content-Type: application/json" \
  -d '{"query": "Tôi muốn mua laptop gaming"}'

# Similar products
curl http://localhost:8008/api/v1/similar/1
```

**Giải thích AI architecture:**
```
"AI Service có 3 components:
1. LSTM Model: Học từ lịch sử mua hàng (241K parameters)
2. Knowledge Graph: Neo4j lưu relationships (160 nodes, 1900+ edges)
3. RAG System: Semantic search với FAISS (384-dim embeddings)

Hybrid engine kết hợp 3 sources với weights:
- LSTM: 30%
- Graph: 30% 
- RAG: 40%"
```

---

### Part 6: Show Technical Details (2-3 phút)

**Terminal demos:**

1. **Show databases**
   ```bash
   # List all databases
   docker-compose ps | grep db
   
   # Show we have 8 databases:
   # 3 MySQL: user, cart, shipping
   # 4 PostgreSQL: product, order, payment, frontend
   # 1 Neo4j: ai-service
   ```

2. **Show API Gateway**
   ```bash
   # Show Nginx config
   cat api-gateway/conf.d/default.conf
   
   # Test via gateway
   curl http://localhost:8080/api/products/ | head -20
   ```

3. **Show JWT tokens (Optional)**
   ```bash
   # Login and get tokens
   curl -X POST http://localhost:8002/api/login/ \
     -H "Content-Type: application/json" \
     -d '{"username": "demo", "password": "demo123"}' | jq
   ```

4. **Show Neo4j Graph (Optional)**
   ```bash
   # Open Neo4j Browser
   open http://localhost:7474
   
   # Login: neo4j / password123
   
   # Run query:
   MATCH (n) RETURN count(n)  // Show 160 nodes
   MATCH ()-[r]->() RETURN count(r)  // Show 1900+ relationships
   
   # Visualize:
   MATCH (u:User)-[:PURCHASED]->(p:Product)
   RETURN u, p
   LIMIT 20
   ```

---

### Part 7: Testing & Quality (1-2 phút)

**Run E2E tests:**
```bash
# Full flow test
./test_full_flow.sh

# Expected output:
# ✓ 20/20 tests PASSED
# - All services healthy
# - User registration/login works
# - Product listing works
# - Order flow works
# - Payment created
# - Shipping created
# - AI recommendations work
```

**Show test coverage:**
```bash
# AI Service tests
cd services/ai-service
ls -la run_phase*.py

# Run phase tests (if time allows)
python3 run_phase8.py  # Deployment tests: 7/7 PASS
```

---

## 🎬 DEMO TIPS

### Trước khi demo
1. ✅ Test toàn bộ flow trước
2. ✅ Chuẩn bị sẵn browser tabs
3. ✅ Có backup demo account
4. ✅ Check internet connection (nếu cần)
5. ✅ Close unnecessary apps

### Trong lúc demo
1. 🎤 Nói rõ ràng, không quá nhanh
2. 👀 Để audience nhìn thấy screen
3. ⏸️ Pause sau mỗi action quan trọng
4. 💬 Giải thích "why" không chỉ "what"
5. 😊 Tự tin, cười nhiều

### Nếu có lỗi
1. 🧘 Bình tĩnh, đừng panic
2. 🔄 Restart service nếu cần: `docker-compose restart [service]`
3. 📝 Explain what happened
4. 💪 Continue với backup plan

---

## 🎯 KEY POINTS TO EMPHASIZE

### Technical Excellence
- ✅ **Microservices:** 7 services độc lập, scale riêng biệt
- ✅ **Multiple Databases:** 3 loại DB (MySQL, PostgreSQL, Neo4j)
- ✅ **AI/ML:** 3 phương pháp recommendation (LSTM, Graph, RAG)
- ✅ **API Gateway:** Centralized routing với Nginx
- ✅ **Security:** JWT authentication, role-based access

### Complete Implementation
- ✅ **Full Flow:** Cart → Order → Payment → Shipping
- ✅ **Domain Models:** Book, Electronics, Fashion
- ✅ **Testing:** 20/20 tests passed (100%)
- ✅ **Documentation:** 100% documented
- ✅ **Production Ready:** Docker deployment

### Innovation
- ✅ **Hybrid AI:** Combine 3 ML approaches
- ✅ **Graph Database:** Neo4j for relationships
- ✅ **RAG System:** Semantic search
- ✅ **Vietnamese Support:** Chatbot hiểu tiếng Việt

---

## ❓ ANTICIPATED QUESTIONS & ANSWERS

### Q1: "Tại sao dùng nhiều loại database?"
**A:** "Mỗi service chọn DB phù hợp nhất với use case:
- MySQL: User, Cart, Shipping (relational data, simple queries)
- PostgreSQL: Product, Order, Payment (complex queries, JSON support)
- Neo4j: AI Service (graph relationships, recommendations)"

### Q2: "Làm sao handle transaction across services?"
**A:** "Hiện tại dùng orchestration-based:
- Order Service làm coordinator
- Call từng service tuần tự
- Rollback nếu có lỗi
Có thể upgrade lên Saga pattern hoặc 2PC cho production."

### Q3: "AI model train như thế nào?"
**A:** "3 models:
- LSTM: Train trên user behavior data (1,731 interactions, 16 epochs)
- Graph: Build từ purchase history (Neo4j Cypher queries)
- RAG: Pre-trained sentence transformer + FAISS indexing
Có thể retrain định kỳ với new data."

### Q4: "Scale như thế nào khi user tăng?"
**A:** "Horizontal scaling:
- Scale mỗi service độc lập với Docker replicas
- Add load balancer (HAProxy/Nginx)
- Database sharding/replication
- Cache layer (Redis)
- Message queue (RabbitMQ) cho async tasks"

### Q5: "Security measures nào được implement?"
**A:** "Multiple layers:
- JWT authentication (60 min access token)
- Role-based access control
- HTTPS (có thể enable)
- CORS configuration
- Input validation
- SQL injection prevention (Django ORM)
- Password hashing"

### Q6: "Monitoring và logging?"
**A:** "Hiện tại:
- Health check endpoints cho mỗi service
- Docker logs
- Error handling và logging

Có thể thêm:
- Prometheus + Grafana
- ELK stack (Elasticsearch, Logstash, Kibana)
- APM (Application Performance Monitoring)"

---

## 📸 SCREENSHOTS TO SHOW

Prepare these screenshots as backup:
1. ✅ Architecture diagram
2. ✅ Docker containers running
3. ✅ Database list
4. ✅ Frontend homepage
5. ✅ Product listing
6. ✅ Cart page
7. ✅ Order detail
8. ✅ AI recommendations
9. ✅ Neo4j graph visualization
10. ✅ Test results (20/20)

---

## 🚨 BACKUP PLANS

### If Docker crashes:
```bash
# Quick restart
docker-compose down
docker-compose up -d
./demo_setup.sh
```

### If demo data missing:
```bash
# Re-run setup
./demo_setup.sh
```

### If service doesn't respond:
```bash
# Restart specific service
docker-compose restart [service-name]

# Check logs
docker-compose logs [service-name]
```

### If browser issues:
- Use incognito mode
- Clear cache
- Use different browser

### If network issues:
- Have screenshots ready
- Show code instead
- Explain verbally

---

## ⏱️ TIME MANAGEMENT

**Strict 15-minute demo:**
- Part 1: Architecture (2 min)
- Part 2: User Flow (2 min)
- Part 3: Products (2 min)
- Part 4: Shopping (4 min)
- Part 5: AI Demo (3 min)
- Part 6: Technical (1 min)
- Part 7: Testing (1 min)

**Extended 20-minute demo:**
- Add more technical details
- Show Neo4j visualization
- Demonstrate API calls
- Show more AI features

---

## 🎉 CLOSING

**Summary points:**
```
"Tóm lại, project đã implement:
✅ 7 microservices với 8 databases
✅ Full e-commerce flow
✅ AI recommendation system (3 approaches)
✅ Docker deployment (17 containers)
✅ Comprehensive testing (20/20 passed)
✅ Production ready

Next steps có thể là:
- Kubernetes deployment
- CI/CD pipeline
- Real-time features
- Mobile app

Thank you! Questions?"
```

---

**📋 Pre-Demo Checklist:**
```
□ Docker running
□ All services healthy
□ Demo data loaded
□ Browser tabs prepared
□ Screenshots ready
□ Backup plans ready
□ Confident and ready!
```

**🎬 GOOD LUCK WITH YOUR DEMO! 🎬**
