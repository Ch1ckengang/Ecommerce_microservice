from django.db import models


class Category(models.Model):
    """
    Django Model -> category database table
    Each field below maps to a database column.
    """

    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "categories"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Product(models.Model):
    """
    Django Model -> product database table
    category_id is stored in the same product-service database only.
    """

    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name="products",
    )
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    sku = models.CharField(max_length=100, unique=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "products"
        ordering = ["-created_at"]

    def __str__(self):
        return self.name


# --- Domain-specific product subtype models (DDD, Chapter 2.3.3) ---

class Book(models.Model):
    """Book product details — OneToOne extends Product"""
    product = models.OneToOneField(Product, on_delete=models.CASCADE, related_name="book_detail")
    author = models.CharField(max_length=255)
    publisher = models.CharField(max_length=255, blank=True)
    isbn = models.CharField(max_length=20, unique=True)

    class Meta:
        db_table = "books"

    def __str__(self):
        return f"Book: {self.product.name}"


class Electronics(models.Model):
    """Electronics product details — OneToOne extends Product"""
    product = models.OneToOneField(Product, on_delete=models.CASCADE, related_name="electronics_detail")
    brand = models.CharField(max_length=100)
    warranty = models.IntegerField(default=12, help_text="Warranty in months")

    class Meta:
        db_table = "electronics"

    def __str__(self):
        return f"Electronics: {self.product.name}"


class Fashion(models.Model):
    """Fashion product details — OneToOne extends Product"""
    product = models.OneToOneField(Product, on_delete=models.CASCADE, related_name="fashion_detail")
    size = models.CharField(max_length=10)
    color = models.CharField(max_length=50)

    class Meta:
        db_table = "fashions"

    def __str__(self):
        return f"Fashion: {self.product.name}"
