from rest_framework import serializers

from .models import Payment


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ["id", "order_id", "idempotency_key", "amount", "provider", "transaction_id", "status", "created_at", "updated_at"]
        read_only_fields = fields


class PaymentCreateSerializer(serializers.Serializer):
    order_id = serializers.IntegerField(min_value=1)
    provider = serializers.ChoiceField(choices=["cod", "bank_transfer"], default="cod", required=False)
