from django.shortcuts import render, redirect
from django.contrib import messages
from django.conf import settings
from django.http import JsonResponse
import json
import requests
from .api_client import (
    UserServiceClient, ProductServiceClient, CartServiceClient,
    OrderServiceClient, ShippingServiceClient, PaymentServiceClient,
    AIServiceClient
)


def home(request):
    """Homepage view"""
    featured_products = []
    recommended_products = []
    
    # Fetch featured products
    try:
        product_client = ProductServiceClient()
        response = product_client.list_products({'limit': 8})
        featured_products = response.get('results', [])[:8]
    except Exception as e:
        print(f"Error fetching featured products: {e}")
        
    # Fetch AI recommendations if logged in
    user_id = request.session.get('user_id')
    token = request.session.get('access_token')
    if user_id and token:
        try:
            ai_client = AIServiceClient()
            recommend_resp = ai_client.get_smart_recommendations(user_id, token, k=4)
            recommendations = recommend_resp.get('recommendations', [])
            for rec in recommendations:
                product_data = rec.get('product')
                if product_data:
                    recommended_products.append(product_data)
        except Exception as e:
            print(f"Error fetching AI recommendations: {e}")
            
    context = {
        'products': featured_products,
        'recommended_products': recommended_products
    }
    return render(request, 'pages/home.html', context)


def chatbot_query(request):
    """Proxy view for AI chatbot query"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST method is allowed'}, status=405)
        
    try:
        body = json.loads(request.body)
        query = body.get('query', '')
        if not query:
            return JsonResponse({'error': 'Query is empty'}, status=400)
            
        ai_client = AIServiceClient()
        response = ai_client.send_chatbot_query(query)
        return JsonResponse(response)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def login_view(request):
    """Login page view"""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        try:
            user_client = UserServiceClient()
            response = user_client.login(username, password)
            
            # Store user info in session
            request.session['user_id'] = response.get('user', {}).get('id')
            request.session['username'] = response.get('user', {}).get('username')
            request.session['email'] = response.get('user', {}).get('email')
            request.session['access_token'] = response.get('access')
            request.session['refresh_token'] = response.get('refresh')
            
            messages.success(request, f'Chào mừng {username}!')
            return redirect('pages:home')
        except requests.exceptions.HTTPError as e:
            messages.error(request, 'Tên đăng nhập hoặc mật khẩu không đúng!')
        except Exception as e:
            messages.error(request, f'Lỗi đăng nhập: {str(e)}')
    
    return render(request, 'pages/auth/login.html')


def register_view(request):
    """Registration page view"""
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password_confirm = request.POST.get('password_confirm')
        
        if password != password_confirm:
            messages.error(request, 'Mật khẩu xác nhận không khớp!')
            return render(request, 'pages/auth/register.html')
        
        try:
            user_client = UserServiceClient()
            response = user_client.register(username, email, password)
            
            messages.success(request, 'Đăng ký thành công! Vui lòng đăng nhập.')
            return redirect('pages:login')
        except requests.exceptions.HTTPError as e:
            error_data = e.response.json() if hasattr(e.response, 'json') else {}
            error_msg = error_data.get('username', [None])[0] or error_data.get('email', [None])[0] or 'Đăng ký thất bại!'
            messages.error(request, error_msg)
        except Exception as e:
            messages.error(request, f'Lỗi đăng ký: {str(e)}')
    
    return render(request, 'pages/auth/register.html')


def logout_view(request):
    """Logout view"""
    request.session.flush()
    messages.success(request, 'Đăng xuất thành công!')
    return redirect('pages:home')


def products_list(request):
    """Products listing page"""
    try:
        product_client = ProductServiceClient()
        
        # Get query parameters
        search = request.GET.get('search', '')
        category = request.GET.get('category', '')
        min_price = request.GET.get('min_price', '')
        max_price = request.GET.get('max_price', '')
        ordering = request.GET.get('ordering', '-created_at')
        page = request.GET.get('page', 1)
        
        # Build params
        params = {
            'page': page,
            'page_size': 12,
            'ordering': ordering
        }
        if search:
            params['search'] = search
        if category:
            params['category'] = category
        if min_price:
            params['min_price'] = min_price
        if max_price:
            params['max_price'] = max_price
        
        response = product_client.list_products(params)
        products = response.get('results', [])
        
        # Get categories - 10 categories
        categories = [
            'Điện thoại & Tablet',
            'Laptop & Máy tính',
            'Âm thanh & Phụ kiện',
            'Thời trang Nam',
            'Thời trang Nữ',
            'Đồ gia dụng',
            'Sách & Văn phòng phẩm',
            'Thể thao & Du lịch',
            'Mẹ & Bé',
            'Làm đẹp & Sức khỏe',
        ]
        
        context = {
            'products': products,
            'categories': categories,
            'search': search,
            'category': category,
            'min_price': min_price,
            'max_price': max_price,
            'ordering': ordering,
            'total': response.get('count', 0),
            'next': response.get('next'),
            'previous': response.get('previous'),
        }
    except Exception as e:
        messages.error(request, f'Lỗi tải sản phẩm: {str(e)}')
        context = {'products': [], 'categories': []}
    
    return render(request, 'pages/products/list.html', context)


def product_detail(request, product_id):
    """Product detail page with AI similar products"""
    try:
        product_client = ProductServiceClient()
        product = product_client.get_product(product_id)
        
        # Get stock info
        try:
            stock_info = product_client.check_stock(product_id)
            product['stock_available'] = stock_info.get('available', 0)
        except:
            product['stock_available'] = product.get('stock', 0)
        
        context = {
            'product': product
        }
        
        # Fetch AI similar products
        try:
            ai_client = AIServiceClient()
            similar_resp = ai_client.get_similar_products(product_id)
            context['similar_products'] = similar_resp.get('data', [])[:4]
        except Exception as e:
            print(f"Similar products note: {e}")
            context['similar_products'] = []
            
    except Exception as e:
        messages.error(request, f'Không tìm thấy sản phẩm!')
        return redirect('pages:products_list')
    
    return render(request, 'pages/products/detail.html', context)


def cart_view(request):
    """Shopping cart page with add/update/remove actions"""
    if not request.session.get('user_id'):
        messages.warning(request, 'Vui lòng đăng nhập để xem giỏ hàng!')
        return redirect('pages:login')
    
    token = request.session.get('access_token')
    
    # Debug: Check if token exists
    if not token:
        messages.error(request, 'Phiên đăng nhập đã hết hạn. Vui lòng đăng nhập lại!')
        return redirect('pages:login')
    
    cart_client = CartServiceClient()
    product_client = ProductServiceClient()
    
    # Handle POST actions (add, update, remove)
    if request.method == 'POST':
        action = request.POST.get('action')
        try:
            if action == 'add':
                product_id = int(request.POST.get('product_id'))
                quantity = int(request.POST.get('quantity', 1))
                product = product_client.get_product(product_id)
                cart = cart_client.get_or_create_cart(token)
                cart_client.add_to_cart(cart['id'], product_id, quantity, str(product.get('price', 0)), token)
                request.session['cart_count'] = request.session.get('cart_count', 0) + quantity
                messages.success(request, 'Đã thêm sản phẩm vào giỏ hàng!')
            elif action == 'update':
                item_id = int(request.POST.get('item_id'))
                quantity = int(request.POST.get('quantity', 1))
                cart_client.update_cart_item(item_id, quantity, token)
                messages.success(request, 'Đã cập nhật số lượng!')
            elif action == 'remove':
                item_id = int(request.POST.get('item_id'))
                cart_client.remove_from_cart(item_id, token)
                messages.success(request, 'Đã xóa sản phẩm khỏi giỏ hàng!')
        except Exception as e:
            messages.error(request, f'Lỗi: {str(e)}')
        return redirect('pages:cart')
    
    # GET — display cart
    try:
        cart = cart_client.get_or_create_cart(token)
        cart_items = cart.get('items', [])
        request.session['cart_count'] = sum(item.get('quantity', 0) for item in cart_items)
        
        # Fetch product details for each item
        for item in cart_items:
            try:
                product = product_client.get_product(item['product_id'])
                item['product'] = product
            except:
                item['product'] = {'name': 'Sản phẩm không xác định', 'price': 0}
        
        # Calculate totals
        subtotal = sum(float(item.get('unit_price', 0)) * item.get('quantity', 0) for item in cart_items)
        
        context = {
            'cart_items': cart_items,
            'subtotal': subtotal,
            'shipping': 30000,
            'total': subtotal + 30000
        }
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 403:
            messages.error(request, 'Phiên đăng nhập đã hết hạn. Vui lòng đăng nhập lại!')
            request.session.flush()
            return redirect('pages:login')
        messages.error(request, f'Lỗi tải giỏ hàng: {str(e)}')
        context = {'cart_items': [], 'subtotal': 0, 'shipping': 0, 'total': 0}
    except Exception as e:
        messages.error(request, f'Lỗi tải giỏ hàng: {str(e)}')
        context = {'cart_items': [], 'subtotal': 0, 'shipping': 0, 'total': 0}
    
    return render(request, 'pages/cart/cart.html', context)


def checkout_view(request):
    """Checkout page — creates order with items from cart, then payment and shipment"""
    if not request.session.get('user_id'):
        messages.warning(request, 'Vui lòng đăng nhập để thanh toán!')
        return redirect('pages:login')
    
    token = request.session.get('access_token')
    if not token:
        messages.error(request, 'Phiên đăng nhập đã hết hạn. Vui lòng đăng nhập lại!')
        return redirect('pages:login')
    
    if request.method == 'POST':
        try:
            shipping_address = request.POST.get('shipping_address', '')
            full_name = request.POST.get('full_name', '').strip()
            phone = request.POST.get('phone', '').strip()
            shipping_method = request.POST.get('shipping_method', 'standard')
            payment_method = request.POST.get('payment_method', 'cod')
            if not shipping_address:
                messages.error(request, 'Vui lòng nhập địa chỉ giao hàng!')
                return redirect('pages:checkout')
            if shipping_method not in {'standard', 'express'}:
                shipping_method = 'standard'
            if payment_method not in {'cod', 'bank_transfer'}:
                payment_method = 'cod'
            
            # 1. Get cart items
            cart_client = CartServiceClient()
            product_client = ProductServiceClient()
            cart = cart_client.get_or_create_cart(token)
            cart_items = cart.get('items', [])
            
            if not cart_items:
                messages.error(request, 'Giỏ hàng trống!')
                return redirect('pages:cart')
            
            # 2. Build order_items with product prices
            order_items = []
            total_amount = 0
            for item in cart_items:
                product = product_client.get_product(item['product_id'])
                price = product.get('price', item.get('unit_price', 0))
                order_items.append({
                    'product_id': item['product_id'],
                    'quantity': item['quantity'],
                })
                total_amount += float(price) * item['quantity']
            
            # 3. Create order
            order_client = OrderServiceClient()
            full_shipping_address = shipping_address
            if full_name or phone:
                full_shipping_address = f"{full_name} - {phone}\n{shipping_address}".strip()
            order_data = {
                'shipping_address': full_shipping_address,
                'shipping_method': shipping_method,
                'order_items': order_items
            }
            order = order_client.create_order(order_data, token)
            order_id = order.get('id')
            
            # 4. Create payment record
            try:
                payment_client = PaymentServiceClient()
                payment_client.create_payment(order_id, payment_method, token)
            except Exception as pe:
                print(f"Payment creation note: {pe}")
            
            # 5. Create shipment record
            try:
                shipping_client = ShippingServiceClient()
                shipping_client.create_shipment(order_id, full_shipping_address, shipping_method, token)
            except Exception as se:
                print(f"Shipment creation note: {se}")
            
            # 6. Clear cart items after successful order
            for item in cart_items:
                try:
                    cart_client.remove_from_cart(item['id'], token)
                except:
                    pass
            request.session['cart_count'] = 0
            
            messages.success(request, f'Đặt hàng thành công! Mã đơn hàng: #{order_id}')
            return redirect('pages:order_detail', order_id=order_id)
        except Exception as e:
            messages.error(request, f'Lỗi đặt hàng: {str(e)}')
    
    # GET — display checkout form with cart summary
    try:
        cart_client = CartServiceClient()
        product_client = ProductServiceClient()
        cart = cart_client.get_or_create_cart(token)
        cart_items = cart.get('items', [])
        
        for item in cart_items:
            try:
                product = product_client.get_product(item['product_id'])
                item['product'] = product
            except:
                item['product'] = {'name': 'Sản phẩm không xác định', 'price': 0}
        
        subtotal = sum(float(item.get('unit_price', 0)) * item.get('quantity', 0) for item in cart_items)
        
        context = {
            'cart_items': cart_items,
            'subtotal': subtotal,
            'shipping': 30000,
            'total': subtotal + 30000
        }
    except Exception as e:
        messages.error(request, f'Lỗi tải thông tin: {str(e)}')
        context = {'cart_items': [], 'subtotal': 0, 'shipping': 0, 'total': 0}
    
    return render(request, 'pages/checkout/checkout.html', context)


def orders_list(request):
    """Orders history page"""
    if not request.session.get('user_id'):
        messages.warning(request, 'Vui lòng đăng nhập để xem đơn hàng!')
        return redirect('pages:login')
    
    token = request.session.get('access_token')
    if not token:
        messages.error(request, 'Phiên đăng nhập đã hết hạn. Vui lòng đăng nhập lại!')
        return redirect('pages:login')
    
    try:
        order_client = OrderServiceClient()
        
        response = order_client.list_orders(token)
        orders = response.get('results', [])
        
        context = {
            'orders': orders
        }
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 403:
            messages.error(request, 'Phiên đăng nhập đã hết hạn. Vui lòng đăng nhập lại!')
            request.session.flush()
            return redirect('pages:login')
        messages.error(request, f'Lỗi tải đơn hàng: {str(e)}')
        context = {'orders': []}
    except Exception as e:
        messages.error(request, f'Lỗi tải đơn hàng: {str(e)}')
        context = {'orders': []}
    
    return render(request, 'pages/orders/list.html', context)


def order_detail(request, order_id):
    """Order detail page"""
    if not request.session.get('user_id'):
        messages.warning(request, 'Vui lòng đăng nhập!')
        return redirect('pages:login')
    
    token = request.session.get('access_token')
    if not token:
        messages.error(request, 'Phiên đăng nhập đã hết hạn. Vui lòng đăng nhập lại!')
        return redirect('pages:login')
    
    try:
        order_client = OrderServiceClient()
        
        order = order_client.get_order(order_id, token)
        
        context = {
            'order': order
        }
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 403:
            messages.error(request, 'Phiên đăng nhập đã hết hạn. Vui lòng đăng nhập lại!')
            request.session.flush()
            return redirect('pages:login')
        messages.error(request, 'Không tìm thấy đơn hàng!')
        return redirect('pages:orders_list')
    except Exception as e:
        messages.error(request, f'Không tìm thấy đơn hàng!')
        return redirect('pages:orders_list')
    
    return render(request, 'pages/orders/detail.html', context)


def profile_view(request):
    """User profile page"""
    if not request.session.get('user_id'):
        messages.warning(request, 'Vui lòng đăng nhập!')
        return redirect('pages:login')
    
    token = request.session.get('access_token')
    if not token:
        messages.error(request, 'Phiên đăng nhập đã hết hạn. Vui lòng đăng nhập lại!')
        return redirect('pages:login')
    
    try:
        user_client = UserServiceClient()
        
        profile = user_client.get_profile(token)
        
        context = {
            'profile': profile
        }
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 403:
            messages.error(request, 'Phiên đăng nhập đã hết hạn. Vui lòng đăng nhập lại!')
            request.session.flush()
            return redirect('pages:login')
        messages.error(request, f'Lỗi tải thông tin: {str(e)}')
        context = {'profile': {}}
    except Exception as e:
        messages.error(request, f'Lỗi tải thông tin: {str(e)}')
        context = {'profile': {}}
    
    return render(request, 'pages/profile/profile.html', context)
