from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.generics import GenericAPIView
from rest_framework.pagination import PageNumberPagination

from product_service.api import paginated_response, success_response
from product_service.permissions import InternalServiceTokenPermission
from .serializers import CategorySerializer, ProductSerializer
from .services import CategoryService, ProductService


class ReadPublicWriteInternalMixin:
    def get_permissions(self):
        if self.request.method in {"GET", "HEAD", "OPTIONS"}:
            return [AllowAny()]
        return [InternalServiceTokenPermission()]


class CategoryListCreateView(ReadPublicWriteInternalMixin, GenericAPIView):
    serializer_class = CategorySerializer
    pagination_class = PageNumberPagination

    def get(self, request):
        queryset = CategoryService.list_categories(request.query_params)
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(queryset, request, view=self)
        serializer = self.get_serializer(page, many=True)
        return paginated_response(paginator, serializer.data, message="Categories fetched successfully.")

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        category = CategoryService.create_category(serializer.validated_data)
        return success_response(
            self.get_serializer(category).data,
            message="Category created successfully.",
            status_code=status.HTTP_201_CREATED,
        )


class CategoryDetailView(ReadPublicWriteInternalMixin, GenericAPIView):
    serializer_class = CategorySerializer

    def get(self, request, category_id):
        category = CategoryService.get_category(category_id)
        return success_response(self.get_serializer(category).data, message="Category fetched successfully.")

    def put(self, request, category_id):
        category = CategoryService.get_category(category_id)
        serializer = self.get_serializer(category, data=request.data)
        serializer.is_valid(raise_exception=True)
        category = CategoryService.update_category(category, serializer.validated_data)
        return success_response(self.get_serializer(category).data, message="Category updated successfully.")

    def delete(self, request, category_id):
        category = CategoryService.get_category(category_id)
        CategoryService.delete_category(category)
        return success_response(message="Category deleted successfully.")


class ProductListCreateView(ReadPublicWriteInternalMixin, GenericAPIView):
    serializer_class = ProductSerializer
    pagination_class = PageNumberPagination

    def get(self, request):
        queryset = ProductService.list_products(request.query_params)
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(queryset, request, view=self)
        serializer = self.get_serializer(page, many=True)
        return paginated_response(paginator, serializer.data, message="Products fetched successfully.")

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        product = ProductService.create_product(serializer.validated_data)
        output = self.get_serializer(product)
        return success_response(output.data, message="Product created successfully.", status_code=status.HTTP_201_CREATED)


class ProductDetailView(ReadPublicWriteInternalMixin, GenericAPIView):
    serializer_class = ProductSerializer

    def get(self, request, product_id):
        product = ProductService.get_product(product_id)
        serializer = self.get_serializer(product)
        return success_response(serializer.data, message="Product fetched successfully.")

    def put(self, request, product_id):
        product = ProductService.get_product(product_id)
        serializer = self.get_serializer(product, data=request.data)
        serializer.is_valid(raise_exception=True)
        updated_product = ProductService.update_product(product, serializer.validated_data)
        output = self.get_serializer(updated_product)
        return success_response(output.data, message="Product updated successfully.")

    def delete(self, request, product_id):
        product = ProductService.get_product(product_id)
        ProductService.delete_product(product)
        return success_response(message="Product deleted successfully.")


class ProductStockCheckView(GenericAPIView):
    """Check stock availability for multiple products"""
    permission_classes = [InternalServiceTokenPermission]
    authentication_classes = []
    
    def post(self, request):
        """
        Expected payload: {"products": [{"product_id": 1, "quantity": 2}, ...]}
        """
        products_data = request.data.get("products", [])
        
        if not products_data:
            return success_response(
                {"available": True, "products": []},
                message="No products to check"
            )
        
        result = ProductService.check_stock_availability(products_data)
        return success_response(result, message="Stock availability checked")


class ProductStockReserveView(GenericAPIView):
    """Reserve stock for products (decrease stock)"""
    permission_classes = [InternalServiceTokenPermission]
    authentication_classes = []
    
    def post(self, request):
        """
        Expected payload: {"products": [{"product_id": 1, "quantity": 2}, ...]}
        """
        products_data = request.data.get("products", [])
        
        if not products_data:
            return success_response(
                {"success": False, "message": "No products to reserve"},
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        result = ProductService.reserve_stock(products_data)
        
        if result["success"]:
            return success_response(result, message="Stock reserved successfully")
        else:
            return success_response(
                result,
                message=result.get("message", "Failed to reserve stock"),
                status_code=status.HTTP_400_BAD_REQUEST
            )


class ProductStockReleaseView(GenericAPIView):
    """Release reserved stock (increase stock back)"""
    permission_classes = [InternalServiceTokenPermission]
    authentication_classes = []
    
    def post(self, request):
        """
        Expected payload: {"products": [{"product_id": 1, "quantity": 2}, ...]}
        """
        products_data = request.data.get("products", [])
        
        if not products_data:
            return success_response(
                {"success": False, "message": "No products to release"},
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        result = ProductService.release_stock(products_data)
        return success_response(result, message="Stock released successfully")
