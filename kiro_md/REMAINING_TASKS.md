# 📋 CÁC TASK CÒN LẠI - HƯỚNG DẪN THỰC HIỆN

**Ngày cập nhật:** 09/06/2026  
**Trạng thái dự án:** 95% hoàn thành ✅  
**Test Score:** 20/20 PASSED ✅

---

## 📊 TỔNG QUAN

Dự án đã hoàn thành 95% với tất cả chức năng cốt lõi hoạt động. Các task còn lại là **tùy chọn** để nâng cao trải nghiệm người dùng và quản lý hệ thống.

### ✅ Đã hoàn thành (Core Features)
- ✅ API Gateway (Nginx)
- ✅ JWT Authentication
- ✅ Full order flow (Cart → Order → Payment → Shipping)
- ✅ 7 microservices với 7 databases riêng biệt
- ✅ AI Service (LSTM + Graph + RAG)
- ✅ Product domains (Book/Electronics/Fashion)
- ✅ 20/20 tests passed
- ✅ **[NEW]** Category filter hiển thị đúng số lượng sản phẩm

---

## ⏳ CÁC TASK CÒN LẠI

### 🟡 MEDIUM PRIORITY

#### Task 1.4: Token Refresh Middleware
**Mô tả:** Auto-refresh JWT token khi gần hết hạn

**File cần sửa:**
- `services/frontend_service/frontend/middleware.py`

**Hướng dẫn:**
```python
# frontend/middleware.py
from datetime import datetime, timedelta
from django.utils.deprecation import MiddlewareMixin
from .utils import refresh_token_if_needed

class TokenRefreshMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if request.user.is_authenticated:
            access_token = request.session.get('access_token')
            refresh_token = request.session.get('refresh_token')
            
            # Check if token expires in next 5 minutes
            expires_at = request.session.get('token_expires_at')
            if expires_at:
                time_left = expires_at - datetime.now().timestamp()
                if time_left < 300:  # 5 minutes
                    # Refresh token
                    new_tokens = refresh_token_if_needed(refresh_token)
                    if new_tokens:
                        request.session['access_token'] = new_tokens['access']
                        request.session['token_expires_at'] = datetime.now().timestamp() + 3600
        
        return None
```

**Thêm vào settings.py:**
```python
MIDDLEWARE = [
    # ... existing middleware
    'frontend.middleware.TokenRefreshMiddleware',  # Add this
]
```

**Ước tính thời gian:** 1-2 giờ

---

#### Task 2.3: Cart Update/Remove Buttons
**Mô tả:** Thêm nút cập nhật số lượng và xóa item trong giỏ hàng

**File cần sửa:**
- `services/frontend_service/templates/cart_detail.html`
- `services/frontend_service/frontend/views.py`

**Hướng dẫn:**

1. **Thêm views trong `frontend/views.py`:**
```python
@login_required
def update_cart_item(request, item_id):
    """Update cart item quantity"""
    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))
        
        # Call cart service API
        response = cart_client.update_item(
            cart_id=request.session.get('cart_id'),
            item_id=item_id,
            quantity=quantity
        )
        
        messages.success(request, 'Đã cập nhật giỏ hàng')
        return redirect('cart_detail')

@login_required
def remove_cart_item(request, item_id):
    """Remove item from cart"""
    # Call cart service API
    response = cart_client.remove_item(
        cart_id=request.session.get('cart_id'),
        item_id=item_id
    )
    
    messages.success(request, 'Đã xóa sản phẩm khỏi giỏ hàng')
    return redirect('cart_detail')
```

2. **Thêm URLs:**
```python
# frontend/urls.py
urlpatterns = [
    # ... existing urls
    path('cart/item/<int:item_id>/update/', views.update_cart_item, name='update_cart_item'),
    path('cart/item/<int:item_id>/remove/', views.remove_cart_item, name='remove_cart_item'),
]
```

3. **Cập nhật template `cart_detail.html`:**
```html
{% for item in cart.items %}
<tr>
    <td>{{ item.product_name }}</td>
    <td>
        <form method="POST" action="{% url 'update_cart_item' item.id %}" style="display: inline;">
            {% csrf_token %}
            <input type="number" name="quantity" value="{{ item.quantity }}" min="1" max="99" style="width: 60px;">
            <button type="submit" class="btn btn-sm btn-primary">Cập nhật</button>
        </form>
    </td>
    <td>{{ item.price }} VNĐ</td>
    <td>{{ item.subtotal }} VNĐ</td>
    <td>
        <form method="POST" action="{% url 'remove_cart_item' item.id %}" style="display: inline;">
            {% csrf_token %}
            <button type="submit" class="btn btn-sm btn-danger" 
                    onclick="return confirm('Bạn có chắc muốn xóa sản phẩm này?')">
                Xóa
            </button>
        </form>
    </td>
</tr>
{% endfor %}
```

**Ước tính thời gian:** 2-3 giờ

---

### 🟢 LOW PRIORITY

#### Task 2.2: Profile Edit UI
**Mô tả:** Cho phép user chỉnh sửa thông tin cá nhân

**File cần tạo/sửa:**
- `templates/profile_edit.html`
- `frontend/views.py`
- `frontend/forms.py`

**Hướng dẫn:**

1. **Tạo form trong `frontend/forms.py`:**
```python
from django import forms

class ProfileEditForm(forms.Form):
    username = forms.CharField(max_length=150, required=False)
    email = forms.EmailField(required=False)
    first_name = forms.CharField(max_length=30, required=False)
    last_name = forms.CharField(max_length=30, required=False)
    phone = forms.CharField(max_length=20, required=False)
    address = forms.CharField(widget=forms.Textarea, required=False)
```

2. **Thêm view:**
```python
@login_required
def profile_edit(request):
    if request.method == 'POST':
        form = ProfileEditForm(request.POST)
        if form.is_valid():
            # Call user service API to update profile
            response = user_client.update_profile(
                user_id=request.user.id,
                data=form.cleaned_data
            )
            messages.success(request, 'Đã cập nhật thông tin')
            return redirect('profile')
    else:
        # Get current profile data
        profile = user_client.get_profile(request.user.id)
        form = ProfileEditForm(initial=profile)
    
    return render(request, 'profile_edit.html', {'form': form})
```

3. **Tạo template `profile_edit.html`:**
```html
{% extends 'base.html' %}

{% block content %}
<div class="container mt-4">
    <h2>Chỉnh sửa thông tin</h2>
    
    <form method="POST" class="mt-4">
        {% csrf_token %}
        
        <div class="form-group">
            <label>Tên đăng nhập</label>
            {{ form.username }}
        </div>
        
        <div class="form-group">
            <label>Email</label>
            {{ form.email }}
        </div>
        
        <div class="form-group">
            <label>Họ</label>
            {{ form.first_name }}
        </div>
        
        <div class="form-group">
            <label>Tên</label>
            {{ form.last_name }}
        </div>
        
        <div class="form-group">
            <label>Số điện thoại</label>
            {{ form.phone }}
        </div>
        
        <div class="form-group">
            <label>Địa chỉ</label>
            {{ form.address }}
        </div>
        
        <button type="submit" class="btn btn-primary">Lưu thay đổi</button>
        <a href="{% url 'profile' %}" class="btn btn-secondary">Hủy</a>
    </form>
</div>
{% endblock %}
```

**Ước tính thời gian:** 2-3 giờ

---

#### Task 3.2: Chatbot với Product Cards
**Mô tả:** Hiển thị sản phẩm dạng cards thay vì text thuần

**File cần sửa:**
- `templates/chatbot.html`

**Hướng dẫn:**

```html
<!-- Thay đổi phần hiển thị response -->
<div class="chatbot-response">
    <div class="message-text">{{ response.text }}</div>
    
    {% if response.products %}
    <div class="product-cards mt-3">
        <div class="row">
            {% for product in response.products %}
            <div class="col-md-4 mb-3">
                <div class="card">
                    {% if product.image %}
                    <img src="{{ product.image }}" class="card-img-top" alt="{{ product.name }}">
                    {% endif %}
                    <div class="card-body">
                        <h5 class="card-title">{{ product.name }}</h5>
                        <p class="card-text">
                            <strong>{{ product.price }} VNĐ</strong>
                        </p>
                        <p class="card-text">
                            <small class="text-muted">{{ product.category }}</small>
                        </p>
                        <a href="{% url 'product_detail' product.id %}" class="btn btn-primary btn-sm">
                            Xem chi tiết
                        </a>
                    </div>
                </div>
            </div>
            {% endfor %}
        </div>
    </div>
    {% endif %}
</div>
```

**CSS bổ sung:**
```css
.product-cards .card {
    height: 100%;
    transition: transform 0.2s;
}

.product-cards .card:hover {
    transform: translateY(-5px);
    box-shadow: 0 4px 8px rgba(0,0,0,0.1);
}

.product-cards .card-img-top {
    height: 200px;
    object-fit: cover;
}
```

**Ước tính thời gian:** 1-2 giờ

---

#### Task 3.3: Live Search Bar
**Mô tả:** Tìm kiếm sản phẩm real-time trên navbar

**File cần sửa:**
- `templates/base.html`
- `frontend/views.py` (thêm API endpoint)

**Hướng dẫn:**

1. **Thêm search bar vào navbar trong `base.html`:**
```html
<nav class="navbar navbar-expand-lg navbar-dark bg-dark">
    <!-- ... existing navbar items ... -->
    
    <div class="search-box">
        <input type="text" id="live-search" class="form-control" placeholder="Tìm kiếm sản phẩm...">
        <div id="search-results" class="search-results-dropdown"></div>
    </div>
</nav>
```

2. **Thêm JavaScript:**
```javascript
<script>
document.getElementById('live-search').addEventListener('input', function(e) {
    const query = e.target.value;
    
    if (query.length < 2) {
        document.getElementById('search-results').innerHTML = '';
        return;
    }
    
    // Call search API
    fetch(`/api/search/?q=${encodeURIComponent(query)}`)
        .then(response => response.json())
        .then(data => {
            const resultsDiv = document.getElementById('search-results');
            
            if (data.results.length === 0) {
                resultsDiv.innerHTML = '<div class="no-results">Không tìm thấy sản phẩm</div>';
                return;
            }
            
            let html = '<ul class="list-group">';
            data.results.forEach(product => {
                html += `
                    <li class="list-group-item">
                        <a href="/products/${product.id}/">
                            <img src="${product.image}" width="40" height="40">
                            ${product.name}
                            <span class="price">${product.price} VNĐ</span>
                        </a>
                    </li>
                `;
            });
            html += '</ul>';
            
            resultsDiv.innerHTML = html;
        });
});
</script>
```

3. **Thêm CSS:**
```css
.search-box {
    position: relative;
    width: 300px;
    margin: 0 20px;
}

.search-results-dropdown {
    position: absolute;
    top: 100%;
    left: 0;
    right: 0;
    background: white;
    border: 1px solid #ddd;
    max-height: 400px;
    overflow-y: auto;
    z-index: 1000;
    display: none;
}

.search-results-dropdown:not(:empty) {
    display: block;
}
```

4. **Thêm view API:**
```python
@require_GET
def search_api(request):
    query = request.GET.get('q', '')
    if len(query) < 2:
        return JsonResponse({'results': []})
    
    # Call product service
    products = product_client.search(query=query, limit=10)
    
    return JsonResponse({
        'results': products
    })
```

**Ước tính thời gian:** 2-3 giờ

---

#### Task 4.2: Demo Setup với Domain Models
**Mô tả:** Mở rộng `demo_setup.sh` để tạo Book/Electronics/Fashion records

**File cần sửa:**
- `demo_setup.sh`

**Hướng dẫn:**

```bash
# Thêm vào demo_setup.sh sau khi tạo products

echo "Creating domain-specific records..."

# Create Books
for i in {1..5}; do
  PRODUCT_ID=$((i))
  curl -X POST http://localhost:8001/api/products/$PRODUCT_ID/book/ \
    -H "Content-Type: application/json" \
    -d '{
      "isbn": "978-0-'$((1000000000 + RANDOM % 1000000000))'",
      "author": "Author '$i'",
      "publisher": "Publisher '$((i % 3 + 1))'",
      "publication_year": '$((2020 + i % 5))',
      "pages": '$((200 + RANDOM % 500))'
    }'
done

# Create Electronics
for i in {6..10}; do
  PRODUCT_ID=$((i))
  curl -X POST http://localhost:8001/api/products/$PRODUCT_ID/electronics/ \
    -H "Content-Type: application/json" \
    -d '{
      "brand": "Brand '$((i % 3 + 1))'",
      "model": "Model-'$i'",
      "warranty_months": '$((12 + (i % 3) * 12))',
      "power_consumption": "'$((50 + RANDOM % 200))'W"
    }'
done

# Create Fashion
for i in {11..15}; do
  PRODUCT_ID=$((i))
  curl -X POST http://localhost:8001/api/products/$PRODUCT_ID/fashion/ \
    -H "Content-Type: application/json" \
    -d '{
      "size": "'$(( ['S', 'M', 'L', 'XL'][RANDOM % 4] ))'",
      "color": "'$(( ['Red', 'Blue', 'Green', 'Black'][RANDOM % 4] ))'",
      "material": "'$(( ['Cotton', 'Polyester', 'Wool'][RANDOM % 3] ))'",
      "gender": "'$(( ['male', 'female', 'unisex'][RANDOM % 3] ))'"
    }'
done

echo "Domain records created!"
```

**Ước tính thời gian:** 1 giờ

---

#### Task 4.3: Payment Button trên Order Detail
**Mô tả:** Thêm nút thanh toán trên trang chi tiết đơn hàng

**File cần sửa:**
- `templates/order_detail.html`
- `frontend/views.py`

**Hướng dẫn:**

1. **Thêm button vào template:**
```html
{% if order.status == 'pending' and not order.payment %}
<div class="alert alert-warning">
    <strong>Đơn hàng chưa thanh toán</strong>
    <form method="POST" action="{% url 'create_payment' order.id %}" class="mt-2">
        {% csrf_token %}
        <div class="form-group">
            <label>Phương thức thanh toán:</label>
            <select name="method" class="form-control" required>
                <option value="credit_card">Thẻ tín dụng</option>
                <option value="bank_transfer">Chuyển khoản</option>
                <option value="cod">Thanh toán khi nhận hàng</option>
            </select>
        </div>
        <button type="submit" class="btn btn-success">Thanh toán ngay</button>
    </form>
</div>
{% endif %}
```

2. **Thêm view:**
```python
@login_required
def create_payment(request, order_id):
    if request.method == 'POST':
        method = request.POST.get('method')
        
        # Call payment service
        payment = payment_client.create_payment(
            order_id=order_id,
            method=method,
            amount=request.POST.get('amount')
        )
        
        messages.success(request, 'Đã tạo thanh toán thành công')
        return redirect('order_detail', order_id=order_id)
```

**Ước tính thời gian:** 1 giờ

---

### 🔵 OPTIONAL

#### Task 6.1-6.3: System Enhancement
**Logging, Admin Dashboard, Docker Cleanup**

Những task này không cần thiết cho demo nhưng tốt cho production:

1. **Logging:** Thêm structured logging với ELK stack
2. **Admin Dashboard:** Django admin tùy chỉnh cho quản lý
3. **Docker Cleanup:** Scripts tự động dọn dẹp volumes, images

**Ước tính thời gian:** 4-8 giờ (mỗi task)

---

## 📊 ĐÁNH GIÁ ƯU TIÊN

### Nên làm trước (nếu có thời gian):
1. ✅ Task 2.3: Cart update/remove (cải thiện UX quan trọng)
2. ✅ Task 1.4: Token refresh (tăng security)
3. ✅ Task 3.3: Live search (UX tốt)

### Có thể bỏ qua:
- Task 2.2: Profile edit (ít dùng)
- Task 3.2: Chatbot cards (cosmetic)
- Task 4.2-4.3: Demo enhancements (không ảnh hưởng chức năng)
- Task 6.x: Optional features

---

## 🎯 KẾT LUẬN

**Dự án đã đạt 95% với tất cả chức năng cốt lõi hoạt động tốt.**

### 🎉 Cập Nhật Mới Nhất (09/06/2026)
- ✅ **Sửa lỗi category filter:** Sản phẩm hiển thị đúng số lượng khi lọc theo danh mục
- ✅ **API mapping:** Sửa `pagination.total` → `pagination.count` trong ProductServiceClient
- ✅ **Test verification:** Đã test thành công với nhiều danh mục khác nhau

Chi tiết: Xem `kiro_md/CATEGORY_FILTER_FIX.md`

Các task còn lại chỉ là **nice-to-have** để nâng cao trải nghiệm. Nếu thời gian có hạn, có thể bỏ qua và tập trung vào:
- Viết tài liệu hướng dẫn sử dụng
- Chuẩn bị demo presentation
- Testing và bug fixes

**Hệ thống hiện tại đã sẵn sàng cho demo và deployment! 🎉**
