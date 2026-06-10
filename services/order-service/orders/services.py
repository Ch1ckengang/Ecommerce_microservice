from django.db import transaction
from decimal import Decimal
from rest_framework.exceptions import NotFound, ValidationError

from order_service.product_client import ProductServiceClient

from .models import Order, OrderItem


class OrderService:
    @staticmethod
    def list_orders(params):
        queryset = Order.objects.prefetch_related("items").all()
        user_id = params.get("user_id")
        status = params.get("status")
        if user_id:
            queryset = queryset.filter(user_id=user_id)
        if status:
            queryset = queryset.filter(status=status)
        return queryset

    @staticmethod
    def get_order(order_id):
        try:
            return Order.objects.prefetch_related("items").get(pk=order_id)
        except Order.DoesNotExist as exc:
            raise NotFound("Order not found.") from exc

    @staticmethod
    def get_by_idempotency_key(idempotency_key: str):
        return Order.objects.prefetch_related("items").filter(idempotency_key=idempotency_key).first()

    @staticmethod
    def create_order(validated_data):
        return Order.objects.create(**validated_data)

    @staticmethod
    def update_order(order, validated_data):
        for field, value in validated_data.items():
            setattr(order, field, value)
        order.save()
        return order

    @staticmethod
    def delete_order(order):
        order.delete()

    @staticmethod
    def get_accessible_order_ids(user_id: int, order_ids: list[int]) -> list[int]:
        if not order_ids:
            return []

        # Preserve input order while avoiding duplicate IDs.
        deduped_order_ids = list(dict.fromkeys(order_ids))
        accessible_ids = set(
            Order.objects.filter(user_id=user_id, id__in=deduped_order_ids).values_list("id", flat=True)
        )
        return [order_id for order_id in deduped_order_ids if order_id in accessible_ids]

    @staticmethod
    def create_order_with_stock_validation(validated_data, items_data):
        if not items_data:
            raise ValidationError({"order_items": "At least one order item is required."})

        product_client = ProductServiceClient()
        shipping_method = validated_data.pop("shipping_method", "standard")
        shipping_fee = {
            "standard": Decimal("30000.00"),
            "express": Decimal("50000.00"),
        }.get(shipping_method, Decimal("30000.00"))
        priced_items = []
        subtotal = Decimal("0.00")
        for item in items_data:
            product = product_client.get_product(item["product_id"])
            try:
                unit_price = Decimal(str(product["price"]))
            except (KeyError, TypeError, ValueError) as exc:
                raise ValidationError({"order_items": f"Product {item['product_id']} has no valid price."}) from exc
            quantity = item["quantity"]
            priced_items.append({**item, "unit_price": unit_price})
            subtotal += unit_price * quantity

        validated_data["status"] = "pending"
        validated_data["total_amount"] = subtotal + shipping_fee

        products_to_check = [
            {"product_id": item["product_id"], "quantity": item["quantity"]}
            for item in priced_items
        ]

        stock_check = product_client.check_stock(products_to_check)
        if not stock_check.get("available", False):
            unavailable = stock_check.get("unavailable", [])
            details = ", ".join(
                [
                    f"{item.get('name', 'Unknown')} (requested: {item.get('requested', 0)}, available: {item.get('available', 0)})"
                    for item in unavailable
                ]
            )
            raise ValidationError({"order_items": f"Insufficient stock for: {details}"})

        stock_reserved = False
        try:
            with transaction.atomic():
                reserve_result = product_client.reserve_stock(products_to_check)
                if not reserve_result.get("success", False):
                    raise ValidationError({"order_items": reserve_result.get("message", "Failed to reserve stock")})

                stock_reserved = True
                order = Order.objects.create(**validated_data)

                OrderItem.objects.bulk_create(
                    [
                        OrderItem(
                            order=order,
                            product_id=item["product_id"],
                            quantity=item["quantity"],
                            unit_price=item["unit_price"],
                        )
                        for item in priced_items
                    ]
                )

                return Order.objects.prefetch_related("items").get(pk=order.pk)
        except Exception:
            if stock_reserved:
                product_client.release_stock(products_to_check)
            raise


class OrderItemService:
    @staticmethod
    def list_items(params):
        queryset = OrderItem.objects.select_related("order").all()
        order_id = params.get("order_id")
        product_id = params.get("product_id")
        if order_id:
            queryset = queryset.filter(order_id=order_id)
        if product_id:
            queryset = queryset.filter(product_id=product_id)
        return queryset

    @staticmethod
    def get_item(item_id):
        try:
            return OrderItem.objects.select_related("order").get(pk=item_id)
        except OrderItem.DoesNotExist as exc:
            raise NotFound("Order item not found.") from exc

    @staticmethod
    def create_item(validated_data):
        return OrderItem.objects.create(**validated_data)

    @staticmethod
    def update_item(item, validated_data):
        for field, value in validated_data.items():
            setattr(item, field, value)
        item.save()
        return item

    @staticmethod
    def delete_item(item):
        item.delete()
