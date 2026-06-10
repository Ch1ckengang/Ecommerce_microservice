from django.urls import path
from . import views

app_name = 'pages'

urlpatterns = [
    # Home
    path('', views.home, name='home'),
    path('chatbot/query/', views.chatbot_query, name='chatbot_query'),
    
    # Auth
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    
    # Products
    path('products/', views.products_list, name='products_list'),
    path('products/<int:product_id>/', views.product_detail, name='product_detail'),
    
    # Cart
    path('cart/', views.cart_view, name='cart'),
    
    # Checkout
    path('checkout/', views.checkout_view, name='checkout'),
    
    # Orders
    path('orders/', views.orders_list, name='orders_list'),
    path('orders/<int:order_id>/', views.order_detail, name='order_detail'),
    
    # Profile
    path('profile/', views.profile_view, name='profile'),
]
