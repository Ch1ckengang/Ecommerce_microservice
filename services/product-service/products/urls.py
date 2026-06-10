from django.urls import path

from .views import (
    CategoryDetailView,
    CategoryListCreateView,
    ProductDetailView,
    ProductListCreateView,
    ProductStockCheckView,
    ProductStockReserveView,
    ProductStockReleaseView,
)

urlpatterns = [
    path("categories/", CategoryListCreateView.as_view(), name="category-list-create"),
    path("categories/<int:category_id>/", CategoryDetailView.as_view(), name="category-detail"),
    path("", ProductListCreateView.as_view(), name="product-list-create"),
    path("<int:product_id>/", ProductDetailView.as_view(), name="product-detail"),
    # Stock management endpoints
    path("stock/check/", ProductStockCheckView.as_view(), name="product-stock-check"),
    path("stock/reserve/", ProductStockReserveView.as_view(), name="product-stock-reserve"),
    path("stock/release/", ProductStockReleaseView.as_view(), name="product-stock-release"),
]
