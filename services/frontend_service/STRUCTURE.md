# Frontend Service - Cấu trúc dự án

## Tổng quan
Frontend Service là một Django application render server-side HTML templates, tích hợp với các backend microservices thông qua REST API.

## Cấu trúc thư mục

```
frontend_service/
├── frontend_service/          # Django project settings
│   ├── __init__.py
│   ├── settings.py           # Cấu hình chính (database, static files, backend URLs)
│   ├── urls.py               # URL routing chính
│   ├── wsgi.py               # WSGI application
│   └── asgi.py               # ASGI application
│
├── pages/                     # Main Django app
│   ├── migrations/           # Database migrations
│   ├── templates/            # HTML templates
│   │   └── pages/
│   │       ├── home.html
│   │       ├── auth/         # Login, Register templates
│   │       ├── products/     # Product list, detail templates
│   │       ├── cart/         # Cart templates
│   │       ├── checkout/     # Checkout templates
│   │       ├── orders/       # Order history templates
│   │       └── profile/      # User profile templates
│   │
│   ├── static/               # App-specific static files
│   │   ├── css/
│   │   ├── js/
│   │   └── images/
│   │
│   ├── api_client.py         # API clients cho backend services
│   ├── views.py              # View controllers
│   ├── urls.py               # App URL routing
│   ├── models.py             # Database models (nếu cần)
│   └── apps.py               # App configuration
│
├── templates/                 # Project-level templates
│   └── base/
│       ├── base.html         # Base template
│       ├── navbar.html       # Navigation bar
│       └── footer.html       # Footer
│
├── static/                    # Project-level static files
│   ├── css/
│   │   └── style.css         # Custom CSS
│   ├── js/
│   │   └── main.js           # Custom JavaScript
│   └── images/               # Images
│
├── staticfiles/              # Collected static files (production)
│
├── manage.py                 # Django management script
├── requirements.txt          # Python dependencies
├── Dockerfile                # Docker configuration
├── entrypoint.sh            # Docker entrypoint script
├── .dockerignore            # Docker ignore file
├── .env.example             # Environment variables template
└── README.md                # Documentation

```

## Các trang chính

### 1. Trang chủ (/)
- Hero banner
- Danh mục sản phẩm
- Sản phẩm nổi bật
- Tính năng nổi bật

### 2. Xác thực
- `/login/` - Đăng nhập
- `/register/` - Đăng ký
- `/logout/` - Đăng xuất

### 3. Sản phẩm
- `/products/` - Danh sách sản phẩm (với filter, search, pagination)
- `/products/<id>/` - Chi tiết sản phẩm

### 4. Giỏ hàng & Thanh toán
- `/cart/` - Giỏ hàng
- `/checkout/` - Thanh toán

### 5. Đơn hàng
- `/orders/` - Lịch sử đơn hàng
- `/orders/<id>/` - Chi tiết đơn hàng

### 6. Tài khoản
- `/profile/` - Thông tin tài khoản

## API Clients

File `pages/api_client.py` chứa các client classes để giao tiếp với backend services:

- `UserServiceClient` - User authentication & profile
- `ProductServiceClient` - Product listing & details
- `CartServiceClient` - Shopping cart management
- `OrderServiceClient` - Order creation & history
- `ShippingServiceClient` - Shipping methods
- `PaymentServiceClient` - Payment methods

## Environment Variables

Xem file `.env.example` để biết các biến môi trường cần thiết:

- `DEBUG` - Debug mode
- `SECRET_KEY` - Django secret key
- `ALLOWED_HOSTS` - Allowed hosts
- `DB_*` - Database configuration
- `*_SERVICE_URL` - Backend service URLs

## Công nghệ sử dụng

- **Django 5.0.1** - Web framework
- **Django REST Framework** - API integration
- **Tailwind CSS** - Styling (via CDN)
- **PostgreSQL** - Database
- **Gunicorn** - WSGI server
- **Docker** - Containerization

## Chạy development server

```bash
# Cài đặt dependencies
pip install -r requirements.txt

# Chạy migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic

# Chạy server
python manage.py runserver 0.0.0.0:8000
```

## Docker

```bash
# Build image
docker build -t frontend-service .

# Run container
docker run -p 8000:8000 --env-file .env frontend-service
```

## Tích hợp với Backend Services

Frontend service giao tiếp với các backend microservices thông qua HTTP REST API:

1. **User Service** (port 8001) - Authentication, user management
2. **Product Service** (port 8002) - Product catalog, stock
3. **Cart Service** (port 8003) - Shopping cart
4. **Order Service** (port 8004) - Order processing
5. **Shipping Service** (port 8005) - Shipping methods
6. **Payment Service** (port 8006) - Payment processing

## Trạng thái hiện tại

✅ **Đã hoàn thành:**
- Cấu trúc dự án cơ bản
- Settings configuration
- URL routing
- Base templates (navbar, footer)
- Homepage template
- View placeholders
- API client classes
- Static files structure
- Docker configuration

⏳ **Chưa hoàn thành (TODO):**
- Implement view logic với API calls
- Tạo các template còn lại (products, cart, checkout, orders, profile)
- Implement authentication flow
- Add form validation
- Error handling
- Loading states
- Responsive design improvements
- JavaScript interactivity
- Image uploads
- Pagination logic
- Search functionality
- Filter functionality

## Bước tiếp theo

1. Implement authentication views (login, register, logout)
2. Tạo product listing page với filters
3. Tạo product detail page
4. Implement cart functionality
5. Tạo checkout flow
6. Implement order management
7. Add user profile page
8. Testing và debugging
9. Deploy với Docker Compose
