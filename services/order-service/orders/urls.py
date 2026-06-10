from django.urls import path

from .views import OrderBatchAccessVerifyView, OrderDetailView, OrderItemDetailView, OrderItemListCreateView, OrderListCreateView

urlpatterns = [
    path("", OrderListCreateView.as_view(), name="order-list-create"),
    path("ownership/verify-batch/", OrderBatchAccessVerifyView.as_view(), name="order-batch-access-verify"),
    path("<int:order_id>/", OrderDetailView.as_view(), name="order-detail"),
    path("items/", OrderItemListCreateView.as_view(), name="order-item-list-create"),
    path("items/<int:item_id>/", OrderItemDetailView.as_view(), name="order-item-detail"),
]
