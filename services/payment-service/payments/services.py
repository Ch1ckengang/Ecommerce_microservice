from rest_framework.exceptions import NotFound

from .models import Payment


class PaymentService:
    @staticmethod
    def list_payments(params):
        queryset = Payment.objects.all()
        order_id = params.get("order_id")
        status = params.get("status")
        if order_id:
            queryset = queryset.filter(order_id=order_id)
        if status:
            queryset = queryset.filter(status=status)
        return queryset

    @staticmethod
    def get_payment(payment_id):
        try:
            return Payment.objects.get(pk=payment_id)
        except Payment.DoesNotExist as exc:
            raise NotFound("Payment not found.") from exc

    @staticmethod
    def get_by_idempotency_key(idempotency_key: str):
        return Payment.objects.filter(idempotency_key=idempotency_key).first()

    @staticmethod
    def create_payment(validated_data):
        return Payment.objects.create(**validated_data)

    @staticmethod
    def update_payment(payment, validated_data):
        for field, value in validated_data.items():
            setattr(payment, field, value)
        payment.save()
        return payment

    @staticmethod
    def delete_payment(payment):
        payment.delete()
