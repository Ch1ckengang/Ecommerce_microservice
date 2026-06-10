from rest_framework import status
from rest_framework.authentication import get_authorization_header
from rest_framework.exceptions import MethodNotAllowed, ValidationError
from rest_framework.generics import GenericAPIView
from rest_framework.pagination import PageNumberPagination
import uuid

from payment_service.api import paginated_response, success_response
from payment_service.order_client import OrderServiceClient
from .serializers import PaymentCreateSerializer, PaymentSerializer
from .services import PaymentService


class PaymentAccessMixin:
    @staticmethod
    def _get_token(request):
        auth = get_authorization_header(request).split()
        if len(auth) == 2:
            return auth[1].decode("utf-8")
        return ""


class PaymentListCreateView(PaymentAccessMixin, GenericAPIView):
    serializer_class = PaymentSerializer
    pagination_class = PageNumberPagination

    def get_serializer_class(self):
        if self.request.method == "POST":
            return PaymentCreateSerializer
        return PaymentSerializer

    def get(self, request):
        queryset = PaymentService.list_payments(request.query_params)
        token = self._get_token(request)
        order_ids = list({payment.order_id for payment in queryset})
        accessible_order_ids = OrderServiceClient.assert_orders_access_batch(order_ids, token)
        filtered_payments = [
            payment
            for payment in queryset
            if payment.order_id in accessible_order_ids
        ]
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(filtered_payments, request, view=self)
        return paginated_response(paginator, self.get_serializer(page, many=True).data, message="Payments fetched successfully.")

    def post(self, request):
        idempotency_key = request.headers.get("Idempotency-Key", "").strip()
        token = self._get_token(request)
        if idempotency_key:
            existing_payment = PaymentService.get_by_idempotency_key(idempotency_key)
            if existing_payment:
                OrderServiceClient.assert_order_access(existing_payment.order_id, token)
                return success_response(
                    self.get_serializer(existing_payment).data,
                    message="Payment request replayed. Returning existing payment.",
                )

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        order = OrderServiceClient.assert_order_access(serializer.validated_data["order_id"], token)
        amount = order.get("total_amount")
        if amount is None:
            raise ValidationError({"order_id": "Verified order does not include total amount."})
        payload = {
            "order_id": serializer.validated_data["order_id"],
            "amount": amount,
            "provider": serializer.validated_data.get("provider", "cod"),
            "transaction_id": f"PAY-{uuid.uuid4().hex[:12].upper()}",
            "status": "pending",
        }
        if idempotency_key:
            payload["idempotency_key"] = idempotency_key
        payment = PaymentService.create_payment(payload)
        return success_response(PaymentSerializer(payment).data, message="Payment created successfully.", status_code=status.HTTP_201_CREATED)


class PaymentDetailView(PaymentAccessMixin, GenericAPIView):
    serializer_class = PaymentSerializer

    def get(self, request, payment_id):
        payment = PaymentService.get_payment(payment_id)
        OrderServiceClient.assert_order_access(payment.order_id, self._get_token(request))
        return success_response(self.get_serializer(payment).data, message="Payment fetched successfully.")

    def put(self, request, payment_id):
        raise MethodNotAllowed("PUT")

    def delete(self, request, payment_id):
        raise MethodNotAllowed("DELETE")
