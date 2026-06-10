from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Shipment",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("order_id", models.BigIntegerField(db_index=True)),
                ("address", models.TextField()),
                ("carrier", models.CharField(max_length=100)),
                ("tracking_number", models.CharField(max_length=150, unique=True)),
                ("status", models.CharField(choices=[("pending", "Pending"), ("packed", "Packed"), ("in_transit", "In Transit"), ("delivered", "Delivered")], default="pending", max_length=20)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={"db_table": "shipments", "ordering": ["-created_at"]},
        ),
    ]
