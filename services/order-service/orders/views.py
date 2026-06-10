from rest_framework import status
from rest_framework.exceptions import MethodNotAllowed, PermissionDenied, ValidationError
from rest_framework.generics import GenericAPIView
from rest_framework.pagination import PageNumberPagination

from order_service.api import paginated_response, success_response
from .serializers import OrderCreateSerializer, OrderItemSerializer, OrderSerializer, OrderUpdateSerializer
from .services import OrderItemService, OrderService


class OrderListCreateView(GenericAPIView):
    serializer_class = OrderSerializer
    pagination_class = PageNumberPagination

    def get_serializer_class(self):
        if self.request.method == "POST":
            return OrderCreateSerializer
        return OrderSerializer

    def get(self, request):
        params = request.query_params.copy()
        params["user_id"] = request.user.id
        queryset = OrderService.list_orders(params)
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(queryset, request, view=self)
        return paginated_response(paginator, self.get_serializer(page, many=True).data, message="Orders fetched successfully.")

    def post(self, request):
        idempotency_key = request.headers.get("Idempotency-Key", "").strip()
        if idempotency_key:
            existing_order = OrderService.get_by_idempotency_key(idempotency_key)
            if existing_order and existing_order.user_id == request.user.id:
                return success_response(
                    self.get_serializer(existing_order).data,
                    message="Order request replayed. Returning existing order.",
                )

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = dict(serializer.validated_data)
        items_data = validated_data.pop("order_items")
        order_payload = {**validated_data, "user_id": request.user.id}
        if idempotency_key:
            order_payload["idempotency_key"] = idempotency_key

        order = OrderService.create_order_with_stock_validation(order_payload, items_data)

        return success_response(OrderSerializer(order).data, message="Order created successfully.", status_code=status.HTTP_201_CREATED)


class OrderDetailView(GenericAPIView):
    serializer_class = OrderSerializer

    def get_serializer_class(self):
        if self.request.method == "PUT":
            return OrderUpdateSerializer
        return OrderSerializer

    def get(self, request, order_id):
        order = OrderService.get_order(order_id)
        self._check_owner(order, request.user.id)
        return success_response(self.get_serializer(order).data, message="Order fetched successfully.")

    def put(self, request, order_id):
        order = OrderService.get_order(order_id)
        self._check_owner(order, request.user.id)
        serializer = self.get_serializer(order, data=request.data)
        serializer.is_valid(raise_exception=True)
        order = OrderService.update_order(order, serializer.validated_data)
        return success_response(OrderSerializer(order).data, message="Order updated successfully.")

    def delete(self, request, order_id):
        raise MethodNotAllowed("DELETE")

    @staticmethod
    def _check_owner(order, user_id):
        if order.user_id != user_id:
            raise PermissionDenied("You do not have access to this order.")


class OrderBatchAccessVerifyView(GenericAPIView):
    def post(self, request):
        order_ids = request.data.get("order_ids", [])
        if not isinstance(order_ids, list):
            raise ValidationError({"order_ids": "Must be a list of integers."})

        try:
            normalized_ids = [int(order_id) for order_id in order_ids]
        except (TypeError, ValueError):
            raise ValidationError({"order_ids": "Must be a list of integers."})

        accessible_order_ids = OrderService.get_accessible_order_ids(request.user.id, normalized_ids)
        return success_response(
            {
                "accessible_order_ids": accessible_order_ids,
                "requested_count": len(normalized_ids),
                "accessible_count": len(accessible_order_ids),
            },
            message="Order access verified successfully.",
        )


class OrderItemListCreateView(GenericAPIView):
    serializer_class = OrderItemSerializer
    pagination_class = PageNumberPagination

    def get(self, request):
        queryset = OrderItemService.list_items(request.query_params).filter(order__user_id=request.user.id)
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(queryset, request, view=self)
        return paginated_response(paginator, self.get_serializer(page, many=True).data, message="Order items fetched successfully.")

    def post(self, request):
        raise MethodNotAllowed("POST")


class OrderItemDetailView(GenericAPIView):
    serializer_class = OrderItemSerializer

    def get(self, request, item_id):
        item = OrderItemService.get_item(item_id)
        self._check_owner(item, request.user.id)
        return success_response(self.get_serializer(item).data, message="Order item fetched successfully.")

    def put(self, request, item_id):
        raise MethodNotAllowed("PUT")

    def delete(self, request, item_id):
        raise MethodNotAllowed("DELETE")

    @staticmethod
    def _check_owner(item, user_id):
        if item.order.user_id != user_id:
            raise PermissionDenied("You do not have access to this order item.")
