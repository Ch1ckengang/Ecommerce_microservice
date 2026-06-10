from rest_framework.exceptions import NotFound

from .models import Cart, CartItem


class CartService:
    @staticmethod
    def list_carts(params):
        queryset = Cart.objects.prefetch_related("items").all()
        user_id = params.get("user_id")
        status = params.get("status")
        if user_id:
            queryset = queryset.filter(user_id=user_id)
        if status:
            queryset = queryset.filter(status=status)
        return queryset

    @staticmethod
    def get_cart(cart_id):
        try:
            return Cart.objects.prefetch_related("items").get(pk=cart_id)
        except Cart.DoesNotExist as exc:
            raise NotFound("Cart not found.") from exc

    @staticmethod
    def create_cart(validated_data):
        return Cart.objects.create(**validated_data)

    @staticmethod
    def update_cart(cart, validated_data):
        for field, value in validated_data.items():
            setattr(cart, field, value)
        cart.save()
        return cart

    @staticmethod
    def delete_cart(cart):
        cart.delete()


class CartItemService:
    @staticmethod
    def list_items(params):
        queryset = CartItem.objects.select_related("cart").all()
        cart_id = params.get("cart_id")
        product_id = params.get("product_id")
        if cart_id:
            queryset = queryset.filter(cart_id=cart_id)
        if product_id:
            queryset = queryset.filter(product_id=product_id)
        return queryset

    @staticmethod
    def get_item(item_id):
        try:
            return CartItem.objects.select_related("cart").get(pk=item_id)
        except CartItem.DoesNotExist as exc:
            raise NotFound("Cart item not found.") from exc

    @staticmethod
    def create_item(validated_data):
        return CartItem.objects.create(**validated_data)

    @staticmethod
    def update_item(item, validated_data):
        for field, value in validated_data.items():
            setattr(item, field, value)
        item.save()
        return item

    @staticmethod
    def delete_item(item):
        item.delete()
