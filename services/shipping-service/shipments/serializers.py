from rest_framework import serializers

from .models import Shipment


class ShipmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shipment
        fields = ["id", "order_id", "idempotency_key", "address", "carrier", "tracking_number", "status", "created_at", "updated_at"]
        read_only_fields = fields


class ShipmentCreateSerializer(serializers.Serializer):
    order_id = serializers.IntegerField(min_value=1)
    address = serializers.CharField()
    carrier = serializers.ChoiceField(choices=["standard", "express"], default="standard", required=False)


class ShipmentUpdateSerializer(serializers.Serializer):
    address = serializers.CharField()
