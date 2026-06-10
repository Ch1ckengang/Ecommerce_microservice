from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Django Model -> users database table
    Each field maps to a MySQL column in user-service only.
    Supports RBAC: admin, staff, customer (Chapter 2.4.2)
    """

    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('staff', 'Staff'),
        ('customer', 'Customer'),
    )

    email = models.EmailField(unique=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='customer')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "users"
        ordering = ["-date_joined"]

    def __str__(self):
        return self.username
