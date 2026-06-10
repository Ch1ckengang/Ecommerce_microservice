from rest_framework import serializers

from .models import Order, OrderItem


class OrderCreateItemSerializer(serializers.Serializer):
    product_id = serializers.IntegerField(min_value=1)
    quantity = serializers.IntegerField(min_value=1)


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ["id", "order", "product_id", "quantity", "unit_price", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = [
            "id",
            "user_id",
            "idempotency_key",
            "status",
            "total_amount",
            "shipping_address",
            "items",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "user_id",
            "idempotency_key",
            "status",
            "total_amount",
            "items",
            "created_at",
            "updated_at",
        ]


class OrderCreateSerializer(serializers.ModelSerializer):
    order_items = OrderCreateItemSerializer(many=True, write_only=True)
    shipping_method = serializers.ChoiceField(choices=["standard", "express"], default="standard", required=False)

    class Meta:
        model = Order
        fields = ["shipping_address", "shipping_method", "order_items"]

    def validate_order_items(self, value):
        if not value:
            raise serializers.ValidationError("At least one order item is required.")
        return value


class OrderUpdateSerializer(serializers.Serializer):
    shipping_address = serializers.CharField()
