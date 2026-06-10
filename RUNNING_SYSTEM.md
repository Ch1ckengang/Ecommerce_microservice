# Hướng dẫn chạy hệ thống E-Commerce

## Tổng quan hệ thống

Hệ thống E-Commerce với kiến trúc microservices bao gồm:

### Backend Services (6 services)
1. **User Service** - Port 8002 - Quản lý người dùng và xác thực
2. **Product Service** - Port 8001 - Quản lý sản phẩm và kho
3. **Cart Service** - Port 8003 - Quản lý giỏ hàng
4. **Order Service** - Port 8004 - Quản lý đơn hàng
5. **Payment Service** - Port 8005 - Xử lý thanh toán
6. **Shipping Service** - Port 8006 - Quản lý vận chuyển

### Frontend Service
7. **Frontend Service** - Port 8007 - Django web application (server-side rendering)

### Infrastructure
- **API Gateway** - Port 8080 - Nginx reverse proxy
- **7 Databases** - PostgreSQL (4) + MySQL (3)

## Yêu cầu hệ thống

- Docker & Docker Compose
- 4GB RAM trở lên
- 10GB disk space

## Khởi động hệ thống

### 1. Clone repository và cấu hình

```bash
# Di chuyển vào thư mục dự án
cd TieuluanS.A&D

# Kiểm tra file .env đã có đầy đủ cấu hình
cat .env
```

### 2. Build và khởi động tất cả services

```bash
# Build tất cả images
docker compose build

# Khởi động tất cả containers
docker compose up -d

# Kiểm tra trạng thái
docker compose ps
```

### 3. Kiểm tra logs

```bash
# Xem logs tất cả services
docker compose logs -f

# Xem logs của một service cụ thể
docker compose logs -f frontend-service
docker compose logs -f product-service
```

## Truy cập hệ thống

### Frontend (Web UI)
- **URL**: http://localhost:8007
- **Mô tả**: Giao diện web người dùng với Django templates

### API Gateway
- **URL**: http://localhost:8080
- **Mô tả**: Điểm truy cập tập trung cho tất cả backend APIs

### Backend Services (Direct Access)

| Service | URL | Swagger Docs |
|---------|-----|--------------|
| User Service | http://localhost:8002 | http://localhost:8002/swagger/ |
| Product Service | http://localhost:8001 | http://localhost:8001/swagger/ |
| Cart Service | http://localhost:8003 | http://localhost:8003/swagger/ |
| Order Service | http://localhost:8004 | http://localhost:8004/swagger/ |
| Payment Service | http://localhost:8005 | http://localhost:8005/swagger/ |
| Shipping Service | http://localhost:8006 | http://localhost:8006/swagger/ |

## Seed dữ liệu demo

```bash
# Tạo user demo và seed products
docker compose exec product-service python manage.py seed_demo_data

# Hoặc chạy script demo_setup.sh
./demo_setup.sh
```

**Demo credentials:**
- Username: `demo`
- Email: `demo@example.com`
- Password: `Demo123!@#`

## Kiểm tra health của services

```bash
# Kiểm tra tất cả services
docker compose ps

# Kiểm tra health endpoint của từng service
curl http://localhost:8001/health/  # Product Service
curl http://localhost:8002/health/  # User Service
curl http://localhost:8003/health/  # Cart Service
curl http://localhost:8004/health/  # Order Service
curl http://localhost:8005/health/  # Payment Service
curl http://localhost:8006/health/  # Shipping Service
curl http://localhost:8007/         # Frontend Service
```

## Dừng hệ thống

```bash
# Dừng tất cả containers (giữ data)
docker compose stop

# Dừng và xóa containers (giữ data)
docker compose down

# Dừng và xóa containers + volumes (xóa hết data)
docker compose down -v
```

## Khởi động lại một service cụ thể

```bash
# Restart một service
docker compose restart frontend-service

# Rebuild và restart
docker compose up -d --build frontend-service
```

## Troubleshooting

### 1. Container không start được

```bash
# Xem logs chi tiết
docker compose logs frontend-service

# Kiểm tra database connection
docker compose exec frontend-service python manage.py check
```

### 2. Port đã được sử dụng

```bash
# Kiểm tra port đang được sử dụng
sudo lsof -i :8007

# Thay đổi port trong .env
FRONTEND_SERVICE_PORT=8008
```

### 3. Database connection error

```bash
# Kiểm tra database đang chạy
docker compose ps | grep db

# Restart database
docker compose restart frontend-db
```

### 4. Static files không load

```bash
# Collect static files lại
docker compose exec frontend-service python manage.py collectstatic --noinput
```

### 5. Xóa và rebuild từ đầu

```bash
# Dừng và xóa tất cả
docker compose down -v

# Xóa images
docker compose down --rmi all

# Build và start lại
docker compose build
docker compose up -d
```

## Cấu trúc containers

```
┌─────────────────────────────────────────────────────────┐
│                    API Gateway (8080)                    │
│                      Nginx Proxy                         │
└─────────────────────────────────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
┌───────▼────────┐  ┌──────▼──────┐  ┌────────▼────────┐
│ User Service   │  │   Product   │  │  Cart Service   │
│   (8002)       │  │  Service    │  │     (8003)      │
│   + MySQL      │  │   (8001)    │  │    + MySQL      │
└────────────────┘  │ + PostgreSQL│  └─────────────────┘
                    └─────────────┘
        ┌───────────────────┼───────────────────┐
        │                   │                   │
┌───────▼────────┐  ┌──────▼──────┐  ┌────────▼────────┐
│ Order Service  │  │  Payment    │  │ Shipping Service│
│   (8004)       │  │  Service    │  │     (8006)      │
│ + PostgreSQL   │  │   (8005)    │  │    + MySQL      │
└────────────────┘  │ + PostgreSQL│  └─────────────────┘
                    └─────────────┘

┌─────────────────────────────────────────────────────────┐
│              Frontend Service (8007)                     │
│           Django Web Application                         │
│              + PostgreSQL                                │
└─────────────────────────────────────────────────────────┘
```

## Monitoring

### Xem resource usage

```bash
# CPU và Memory usage
docker stats

# Disk usage
docker system df
```

### Xem logs real-time

```bash
# Tất cả services
docker compose logs -f

# Chỉ frontend
docker compose logs -f frontend-service

# Chỉ backend services
docker compose logs -f product-service user-service cart-service order-service
```

## Development workflow

### 1. Chỉnh sửa code

Code được mount vào container qua volumes, nên bạn có thể edit trực tiếp:

```bash
# Edit file
vim services/frontend_service/pages/views.py

# Restart service để apply changes
docker compose restart frontend-service
```

### 2. Chạy migrations

```bash
# Tạo migrations
docker compose exec frontend-service python manage.py makemigrations

# Apply migrations
docker compose exec frontend-service python manage.py migrate
```

### 3. Truy cập Django shell

```bash
docker compose exec frontend-service python manage.py shell
```

### 4. Tạo superuser

```bash
docker compose exec frontend-service python manage.py createsuperuser
```

## Trạng thái hiện tại

✅ **Đã hoàn thành:**
- 6 Backend microservices đang chạy healthy
- Frontend service đang chạy healthy
- 7 Databases đang chạy healthy
- API Gateway đang chạy
- Tất cả services có Swagger documentation
- Demo data đã được seed

✅ **Frontend Service:**
- Django 5.0.1 với server-side rendering
- Base templates (navbar, footer)
- Homepage đã hoàn thành
- API clients cho tất cả backend services
- Static files (CSS, JS) đã setup
- Docker configuration hoàn chỉnh

⏳ **Cần hoàn thiện:**
- Implement các trang còn lại (products, cart, checkout, orders, profile)
- Implement authentication flow
- Kết nối frontend với backend APIs
- Add form validation
- Improve UI/UX

## Các bước tiếp theo

1. **Implement Authentication Pages**
   - Login page với form validation
   - Register page
   - Logout functionality
   - Session management

2. **Implement Product Pages**
   - Product listing với filters và search
   - Product detail page
   - Category filtering

3. **Implement Shopping Cart**
   - Add to cart functionality
   - Update quantity
   - Remove items
   - Cart summary

4. **Implement Checkout Flow**
   - Shipping information form
   - Payment method selection
   - Order confirmation

5. **Implement Order Management**
   - Order history
   - Order detail
   - Order tracking

6. **Testing & Debugging**
   - Test tất cả flows
   - Fix bugs
   - Optimize performance

## Liên hệ & Support

Nếu gặp vấn đề, kiểm tra:
1. Logs của service: `docker compose logs [service-name]`
2. Database connection
3. Environment variables trong .env
4. Port conflicts

---

**Hệ thống đã sẵn sàng để phát triển tiếp!** 🚀
