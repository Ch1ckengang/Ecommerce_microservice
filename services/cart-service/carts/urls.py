from django.urls import path

from .views import CartDetailView, CartItemDetailView, CartItemListCreateView, CartListCreateView

urlpatterns = [
    path("carts/", CartListCreateView.as_view(), name="cart-list-create"),
    path("carts/<int:cart_id>/", CartDetailView.as_view(), name="cart-detail"),
    path("items/", CartItemListCreateView.as_view(), name="cart-item-list-create"),
    path("items/<int:item_id>/", CartItemDetailView.as_view(), name="cart-item-detail"),
]
