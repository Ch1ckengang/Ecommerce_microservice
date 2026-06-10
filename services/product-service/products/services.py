from decimal import Decimal, InvalidOperation

from django.db.models.deletion import ProtectedError
from django.db.models import QuerySet
from rest_framework.exceptions import NotFound, ValidationError

from .models import Category, Product


class CategoryService:
    @staticmethod
    def list_categories(params) -> QuerySet[Category]:
        queryset = Category.objects.all()
        search = params.get("search")
        if search:
            queryset = queryset.filter(name__icontains=search)
        return queryset

    @staticmethod
    def create_category(validated_data):
        return Category.objects.create(**validated_data)

    @staticmethod
    def get_category(category_id: int) -> Category:
        try:
            return Category.objects.get(pk=category_id)
        except Category.DoesNotExist as exc:
            raise NotFound("Category not found.") from exc

    @staticmethod
    def update_category(category: Category, validated_data):
        for field, value in validated_data.items():
            setattr(category, field, value)
        category.save()
        return category

    @staticmethod
    def delete_category(category: Category):
        try:
            category.delete()
        except ProtectedError as exc:
            raise ValidationError({"category": "Cannot delete category with existing products."}) from exc


class ProductService:
    @staticmethod
    def list_products(params) -> QuerySet[Product]:
        queryset = Product.objects.select_related("category").all()

        category_param = params.get("category")
        is_active = params.get("is_active")
        min_price = params.get("min_price") or params.get("price_min")
        max_price = params.get("max_price") or params.get("price_max")
        search = params.get("search")
        ordering = params.get("ordering")

        if category_param:
            # Support both category ID (number) and category name (string)
            try:
                # Try to convert to int (category ID)
                category_id = int(category_param)
                queryset = queryset.filter(category_id=category_id)
            except (ValueError, TypeError):
                # If not a number, treat as category name
                queryset = queryset.filter(category__name__iexact=category_param)

        if is_active is not None:
            normalized = str(is_active).strip().lower()
            if normalized in {"true", "1"}:
                queryset = queryset.filter(is_active=True)
            elif normalized in {"false", "0"}:
                queryset = queryset.filter(is_active=False)
            else:
                raise ValidationError({"is_active": "Use true, false, 1, or 0."})

        if min_price:
            queryset = queryset.filter(price__gte=ProductService._parse_decimal("min_price", min_price))

        if max_price:
            queryset = queryset.filter(price__lte=ProductService._parse_decimal("max_price", max_price))

        if search:
            queryset = queryset.filter(name__icontains=search)

        if ordering:
            allowed_ordering = {
                "name",
                "-name",
                "price",
                "-price",
                "created_at",
                "-created_at",
            }
            if ordering not in allowed_ordering:
                raise ValidationError({"ordering": "Unsupported ordering field."})
            queryset = queryset.order_by(ordering)

        return queryset

    @staticmethod
    def create_product(validated_data):
        return Product.objects.create(**validated_data)

    @staticmethod
    def get_product(product_id: int) -> Product:
        try:
            return Product.objects.select_related("category").get(pk=product_id)
        except Product.DoesNotExist as exc:
            raise NotFound("Product not found.") from exc

    @staticmethod
    def update_product(product: Product, validated_data):
        for field, value in validated_data.items():
            setattr(product, field, value)
        product.save()
        product.refresh_from_db()
        return product

    @staticmethod
    def delete_product(product: Product):
        product.delete()

    @staticmethod
    def _parse_decimal(field_name: str, value: str) -> Decimal:
        try:
            return Decimal(value)
        except (InvalidOperation, TypeError) as exc:
            raise ValidationError({field_name: "Enter a valid decimal value."}) from exc


    @staticmethod
    def check_stock_availability(products_data):
        """
        Check if requested quantities are available for products
        products_data: [{"product_id": 1, "quantity": 2}, ...]
        Returns: {"available": bool, "products": [...], "unavailable": [...]}
        """
        available_products = []
        unavailable_products = []
        
        for item in products_data:
            product_id = item.get("product_id")
            quantity = item.get("quantity", 1)
            
            try:
                product = Product.objects.get(pk=product_id, is_active=True)
                
                if product.stock >= quantity:
                    available_products.append({
                        "product_id": product.id,
                        "name": product.name,
                        "requested": quantity,
                        "available": product.stock
                    })
                else:
                    unavailable_products.append({
                        "product_id": product.id,
                        "name": product.name,
                        "requested": quantity,
                        "available": product.stock
                    })
            except Product.DoesNotExist:
                unavailable_products.append({
                    "product_id": product_id,
                    "name": "Unknown",
                    "requested": quantity,
                    "available": 0,
                    "error": "Product not found"
                })
        
        return {
            "available": len(unavailable_products) == 0,
            "products": available_products,
            "unavailable": unavailable_products
        }

    @staticmethod
    def reserve_stock(products_data):
        """
        Reserve stock by decreasing product quantities
        products_data: [{"product_id": 1, "quantity": 2}, ...]
        Returns: {"success": bool, "message": str, "reserved": [...]}
        """
        from django.db import transaction
        
        # First check availability
        availability = ProductService.check_stock_availability(products_data)
        
        if not availability["available"]:
            return {
                "success": False,
                "message": "Insufficient stock for some products",
                "unavailable": availability["unavailable"]
            }
        
        # Reserve stock in a transaction
        reserved_products = []
        try:
            with transaction.atomic():
                for item in products_data:
                    product_id = item.get("product_id")
                    quantity = item.get("quantity", 1)
                    
                    product = Product.objects.select_for_update().get(pk=product_id)
                    
                    if product.stock < quantity:
                        raise ValidationError(f"Insufficient stock for product {product.name}")
                    
                    product.stock -= quantity
                    product.save()
                    
                    reserved_products.append({
                        "product_id": product.id,
                        "name": product.name,
                        "quantity_reserved": quantity,
                        "remaining_stock": product.stock
                    })
            
            return {
                "success": True,
                "message": "Stock reserved successfully",
                "reserved": reserved_products
            }
        except Exception as e:
            return {
                "success": False,
                "message": str(e),
                "reserved": []
            }

    @staticmethod
    def release_stock(products_data):
        """
        Release stock by increasing product quantities back
        products_data: [{"product_id": 1, "quantity": 2}, ...]
        Returns: {"success": bool, "message": str, "released": [...]}
        """
        from django.db import transaction
        
        released_products = []
        try:
            with transaction.atomic():
                for item in products_data:
                    product_id = item.get("product_id")
                    quantity = item.get("quantity", 1)
                    
                    try:
                        product = Product.objects.select_for_update().get(pk=product_id)
                        product.stock += quantity
                        product.save()
                        
                        released_products.append({
                            "product_id": product.id,
                            "name": product.name,
                            "quantity_released": quantity,
                            "new_stock": product.stock
                        })
                    except Product.DoesNotExist:
                        # Skip non-existent products
                        continue
            
            return {
                "success": True,
                "message": "Stock released successfully",
                "released": released_products
            }
        except Exception as e:
            return {
                "success": False,
                "message": str(e),
                "released": []
            }
