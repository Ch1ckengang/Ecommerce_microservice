from rest_framework import status
from rest_framework.authentication import get_authorization_header
from rest_framework.exceptions import MethodNotAllowed
from rest_framework.generics import GenericAPIView
from rest_framework.pagination import PageNumberPagination
import uuid

from shipping_service.api import paginated_response, success_response
from shipping_service.order_client import OrderServiceClient
from .serializers import ShipmentCreateSerializer, ShipmentSerializer, ShipmentUpdateSerializer
from .services import ShipmentService


class ShipmentAccessMixin:
    @staticmethod
    def _get_token(request):
        auth = get_authorization_header(request).split()
        if len(auth) == 2:
            return auth[1].decode("utf-8")
        return ""


class ShipmentListCreateView(ShipmentAccessMixin, GenericAPIView):
    serializer_class = ShipmentSerializer
    pagination_class = PageNumberPagination

    def get_serializer_class(self):
        if self.request.method == "POST":
            return ShipmentCreateSerializer
        return ShipmentSerializer

    def get(self, request):
        queryset = ShipmentService.list_shipments(request.query_params)
        token = self._get_token(request)
        order_ids = list({shipment.order_id for shipment in queryset})
        accessible_order_ids = OrderServiceClient.assert_orders_access_batch(order_ids, token)
        filtered_shipments = [
            shipment
            for shipment in queryset
            if shipment.order_id in accessible_order_ids
        ]
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(filtered_shipments, request, view=self)
        return paginated_response(paginator, self.get_serializer(page, many=True).data, message="Shipments fetched successfully.")

    def post(self, request):
        idempotency_key = request.headers.get("Idempotency-Key", "").strip()
        token = self._get_token(request)
        if idempotency_key:
            existing_shipment = ShipmentService.get_by_idempotency_key(idempotency_key)
            if existing_shipment:
                OrderServiceClient.assert_order_access(existing_shipment.order_id, token)
                return success_response(
                    self.get_serializer(existing_shipment).data,
                    message="Shipment request replayed. Returning existing shipment.",
                )

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        OrderServiceClient.assert_order_access(serializer.validated_data["order_id"], token)
        payload = {
            "order_id": serializer.validated_data["order_id"],
            "address": serializer.validated_data["address"],
            "carrier": serializer.validated_data.get("carrier", "standard"),
            "tracking_number": f"TRK-{uuid.uuid4().hex[:12].upper()}",
            "status": "pending",
        }
        if idempotency_key:
            payload["idempotency_key"] = idempotency_key
        shipment = ShipmentService.create_shipment(payload)
        return success_response(ShipmentSerializer(shipment).data, message="Shipment created successfully.", status_code=status.HTTP_201_CREATED)


class ShipmentDetailView(ShipmentAccessMixin, GenericAPIView):
    serializer_class = ShipmentSerializer

    def get_serializer_class(self):
        if self.request.method == "PUT":
            return ShipmentUpdateSerializer
        return ShipmentSerializer

    def get(self, request, shipment_id):
        shipment = ShipmentService.get_shipment(shipment_id)
        OrderServiceClient.assert_order_access(shipment.order_id, self._get_token(request))
        return success_response(self.get_serializer(shipment).data, message="Shipment fetched successfully.")

    def put(self, request, shipment_id):
        shipment = ShipmentService.get_shipment(shipment_id)
        serializer = self.get_serializer(shipment, data=request.data)
        serializer.is_valid(raise_exception=True)
        OrderServiceClient.assert_order_access(shipment.order_id, self._get_token(request))
        shipment = ShipmentService.update_shipment(shipment, serializer.validated_data)
        return success_response(ShipmentSerializer(shipment).data, message="Shipment updated successfully.")

    def delete(self, request, shipment_id):
        raise MethodNotAllowed("DELETE")
