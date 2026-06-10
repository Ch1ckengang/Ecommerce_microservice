from django.db import models


class Shipment(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("packed", "Packed"),
        ("in_transit", "In Transit"),
        ("delivered", "Delivered"),
    ]

    order_id = models.BigIntegerField(db_index=True)
    idempotency_key = models.CharField(max_length=80, unique=True, null=True, blank=True)
    address = models.TextField()
    carrier = models.CharField(max_length=100)
    tracking_number = models.CharField(max_length=150, unique=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "shipments"
        ordering = ["-created_at"]
