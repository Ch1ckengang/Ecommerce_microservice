from rest_framework import status
from rest_framework.exceptions import PermissionDenied
from rest_framework.generics import GenericAPIView
from rest_framework.pagination import PageNumberPagination

from cart_service.api import paginated_response, success_response
from .serializers import CartItemSerializer, CartSerializer
from .services import CartItemService, CartService


class CartListCreateView(GenericAPIView):
    serializer_class = CartSerializer
    pagination_class = PageNumberPagination

    def get(self, request):
        params = request.query_params.copy()
        params["user_id"] = request.user.id
        queryset = CartService.list_carts(params)
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(queryset, request, view=self)
        serializer = self.get_serializer(page, many=True)
        return paginated_response(paginator, serializer.data, message="Carts fetched successfully.")

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        cart = CartService.create_cart({**serializer.validated_data, "user_id": request.user.id})
        return success_response(self.get_serializer(cart).data, message="Cart created successfully.", status_code=status.HTTP_201_CREATED)


class CartDetailView(GenericAPIView):
    serializer_class = CartSerializer

    def get(self, request, cart_id):
        cart = CartService.get_cart(cart_id)
        self._check_owner(cart, request.user.id)
        return success_response(self.get_serializer(cart).data, message="Cart fetched successfully.")

    def put(self, request, cart_id):
        cart = CartService.get_cart(cart_id)
        self._check_owner(cart, request.user.id)
        serializer = self.get_serializer(cart, data=request.data)
        serializer.is_valid(raise_exception=True)
        cart = CartService.update_cart(cart, serializer.validated_data)
        return success_response(self.get_serializer(cart).data, message="Cart updated successfully.")

    def delete(self, request, cart_id):
        cart = CartService.get_cart(cart_id)
        self._check_owner(cart, request.user.id)
        CartService.delete_cart(cart)
        return success_response(message="Cart deleted successfully.")

    @staticmethod
    def _check_owner(cart, user_id):
        if cart.user_id != user_id:
            raise PermissionDenied("You do not have access to this cart.")


class CartItemListCreateView(GenericAPIView):
    serializer_class = CartItemSerializer
    pagination_class = PageNumberPagination

    def get(self, request):
        params = request.query_params.copy()
        queryset = CartItemService.list_items(params).filter(cart__user_id=request.user.id)
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(queryset, request, view=self)
        serializer = self.get_serializer(page, many=True)
        return paginated_response(paginator, serializer.data, message="Cart items fetched successfully.")

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        cart = CartService.get_cart(serializer.validated_data["cart"].id)
        if cart.user_id != request.user.id:
            raise PermissionDenied("You can only add items to your own cart.")
        item = CartItemService.create_item(serializer.validated_data)
        return success_response(self.get_serializer(item).data, message="Cart item created successfully.", status_code=status.HTTP_201_CREATED)


class CartItemDetailView(GenericAPIView):
    serializer_class = CartItemSerializer

    def get(self, request, item_id):
        item = CartItemService.get_item(item_id)
        self._check_owner(item, request.user.id)
        return success_response(self.get_serializer(item).data, message="Cart item fetched successfully.")

    def put(self, request, item_id):
        item = CartItemService.get_item(item_id)
        self._check_owner(item, request.user.id)
        serializer = self.get_serializer(item, data=request.data)
        serializer.is_valid(raise_exception=True)
        cart = serializer.validated_data.get("cart", item.cart)
        if cart.user_id != request.user.id:
            raise PermissionDenied("You can only move items within your own cart.")
        item = CartItemService.update_item(item, serializer.validated_data)
        return success_response(self.get_serializer(item).data, message="Cart item updated successfully.")

    def delete(self, request, item_id):
        item = CartItemService.get_item(item_id)
        self._check_owner(item, request.user.id)
        CartItemService.delete_item(item)
        return success_response(message="Cart item deleted successfully.")

    @staticmethod
    def _check_owner(item, user_id):
        if item.cart.user_id != user_id:
            raise PermissionDenied("You do not have access to this cart item.")
