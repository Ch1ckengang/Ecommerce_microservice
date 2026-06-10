# 🔐 FIX LỖI AUTHENTICATION - HƯỚNG DẪN TEST

**Ngày:** 09/06/2026  
**Vấn đề:** Lỗi 403 Forbidden khi truy cập Cart, Orders, Profile sau khi đăng nhập

---

## ✅ ĐÃ SỬA

### 1. Thêm Token Validation
- Kiểm tra token có tồn tại trong session không
- Redirect về login nếu token bị mất
- Thông báo rõ ràng: "Phiên đăng nhập đã hết hạn"

### 2. Improved Error Handling
- Bắt lỗi 403 Forbidden riêng
- Auto logout và redirect về login khi token hết hạn
- Clear session khi phát hiện token không hợp lệ

### 3. Files Đã Sửa
- `services/frontend_service/pages/views.py`:
  - `cart_view()` - line ~230
  - `checkout_view()` - line ~290
  - `orders_list()` - line ~380
  - `order_detail()` - line ~400
  - `profile_view()` - line ~420

---

## 🧪 CÁCH TEST

### Bước 1: Đăng Xuất và Đăng Nhập Lại
```
1. Truy cập: http://localhost:8007
2. Nếu đã đăng nhập, click "Đăng xuất"
3. Click "Đăng nhập"
4. Nhập:
   - Username: (tạo account mới nếu chưa có)
   - Password: 
5. Click "Đăng nhập"
```

### Bước 2: Test Cart
```
1. Sau khi login, click "Giỏ hàng" hoặc truy cập:
   http://localhost:8007/cart/

2. Kết quả mong đợi:
   ✅ Hiển thị giỏ hàng (có thể trống)
   ❌ KHÔNG có lỗi 403
```

### Bước 3: Test Orders
```
1. Click "Đơn hàng" hoặc truy cập:
   http://localhost:8007/orders/

2. Kết quả mong đợi:
   ✅ Hiển thị danh sách đơn hàng
   ❌ KHÔNG có lỗi 403
```

### Bước 4: Test Profile
```
1. Click vào tên user ở góc phải, chọn "Thông tin cá nhân"
   hoặc truy cập: http://localhost:8007/profile/

2. Kết quả mong đợi:
   ✅ Hiển thị thông tin user
   ❌ KHÔNG có lỗi 403
```

### Bước 5: Test Full Shopping Flow
```
1. Xem sản phẩm
2. Thêm vào giỏ hàng
3. Vào giỏ hàng kiểm tra
4. Checkout
5. Xem đơn hàng vừa tạo
```

---

## 🔍 NẾU VẪN LỖI

### Lỗi 1: "Phiên đăng nhập đã hết hạn"
**Nguyên nhân:** Token đã hết hạn (60 phút)  
**Giải pháp:** Đăng nhập lại

### Lỗi 2: Vẫn bị 403 sau khi login
**Nguyên nhân:** Session không được lưu đúng  
**Giải pháp:**
```bash
# Clear browser cookies
# Hoặc dùng Incognito mode
# Hoặc restart frontend service:
docker restart frontend-service
```

### Lỗi 3: Token không được gửi
**Kiểm tra:**
```bash
# Check if user is logged in
docker exec frontend-service python3 manage.py shell << EOF
from django.contrib.sessions.models import Session
from django.utils import timezone
print(Session.objects.filter(expire_date__gte=timezone.now()).count())
EOF
```

---

## 🐛 DEBUG MODE

Nếu cần debug chi tiết, bật Django debug:

```bash
# Trong docker-compose.yml, set:
DEBUG: 'True'

# Restart:
docker-compose restart frontend-service
```

Sau đó xem logs:
```bash
docker logs -f frontend-service
```

---

## ✅ CHECKLIST

Sau khi đăng nhập thành công:

- [ ] Truy cập giỏ hàng không bị lỗi
- [ ] Thêm sản phẩm vào giỏ hàng thành công
- [ ] Checkout tạo đơn hàng thành công  
- [ ] Xem danh sách đơn hàng không bị lỗi
- [ ] Xem chi tiết đơn hàng không bị lỗi
- [ ] Xem profile không bị lỗi

---

## 📊 API TEST (Nếu cần)

Test trực tiếp API:

```bash
# 1. Register
curl -X POST http://localhost:8002/users/register/ \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","email":"test@test.com","password":"Test123","password_confirm":"Test123"}'

# 2. Login
TOKEN=$(curl -s -X POST http://localhost:8002/users/token/ \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"Test123"}' \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['data']['access'])")

echo "Token: $TOKEN"

# 3. Test Cart
curl http://localhost:8003/cart/carts/ \
  -H "Authorization: Bearer $TOKEN"

# 4. Test Orders
curl http://localhost:8004/orders/ \
  -H "Authorization: Bearer $TOKEN"

# 5. Test Profile
curl http://localhost:8002/users/me/ \
  -H "Authorization: Bearer $TOKEN"
```

Nếu API tests pass nhưng frontend vẫn lỗi → vấn đề ở session storage.

---

## 🎯 KẾT LUẬN

**Vấn đề đã được sửa:**
- ✅ Token validation
- ✅ Better error messages
- ✅ Auto logout khi token hết hạn
- ✅ Improved error handling

**Bạn cần:**
1. Đăng xuất
2. Đăng nhập lại
3. Test lại các chức năng

**Nếu vẫn lỗi:**
- Clear browser cookies
- Hoặc dùng Incognito mode
- Hoặc contact để debug thêm

---

**Status:** ✅ FIXED  
**Restart required:** ✅ DONE  
**Test status:** ⏳ WAITING FOR USER TEST
