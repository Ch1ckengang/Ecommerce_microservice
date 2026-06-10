from rest_framework.exceptions import NotFound

from .models import Shipment


class ShipmentService:
    @staticmethod
    def list_shipments(params):
        queryset = Shipment.objects.all()
        order_id = params.get("order_id")
        status = params.get("status")
        if order_id:
            queryset = queryset.filter(order_id=order_id)
        if status:
            queryset = queryset.filter(status=status)
        return queryset

    @staticmethod
    def get_shipment(shipment_id):
        try:
            return Shipment.objects.get(pk=shipment_id)
        except Shipment.DoesNotExist as exc:
            raise NotFound("Shipment not found.") from exc

    @staticmethod
    def get_by_idempotency_key(idempotency_key: str):
        return Shipment.objects.filter(idempotency_key=idempotency_key).first()

    @staticmethod
    def create_shipment(validated_data):
        return Shipment.objects.create(**validated_data)

    @staticmethod
    def update_shipment(shipment, validated_data):
        for field, value in validated_data.items():
            setattr(shipment, field, value)
        shipment.save()
        return shipment

    @staticmethod
    def delete_shipment(shipment):
        shipment.delete()
