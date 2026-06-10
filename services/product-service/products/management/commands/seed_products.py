from django.core.management.base import BaseCommand

from products.models import Category, Product


class Command(BaseCommand):
    help = "Seed initial categories and products for local development."

    def handle(self, *args, **options):
        electronics, _ = Category.objects.get_or_create(
            name="Electronics",
            defaults={"description": "Electronic devices and accessories."},
        )
        books, _ = Category.objects.get_or_create(
            name="Books",
            defaults={"description": "Fiction, non-fiction, and technical books."},
        )

        Product.objects.get_or_create(
            sku="SKU-HEADPHONE-001",
            defaults={
                "category": electronics,
                "name": "Wireless Headphones",
                "description": "Noise-cancelling over-ear headphones.",
                "price": "129.99",
                "stock": 25,
                "is_active": True,
            },
        )
        Product.objects.get_or_create(
            sku="SKU-DJANGO-BOOK-001",
            defaults={
                "category": books,
                "name": "Django Architecture Guide",
                "description": "A practical book on Django service design.",
                "price": "39.90",
                "stock": 40,
                "is_active": True,
            },
        )

        self.stdout.write(self.style.SUCCESS("Seed data ensured."))
