import uuid

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Order",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("customer_id", models.UUIDField()),
                ("status", models.CharField(choices=[("pending_payment", "Pending payment"), ("paid", "Paid"), ("confirmed", "Confirmed"), ("packed", "Packed"), ("shipped", "Shipped"), ("completed", "Completed"), ("cancelled", "Cancelled"), ("refunded", "Refunded")], default="pending_payment", max_length=32)),
                ("currency", models.CharField(default="VND", max_length=3)),
                ("subtotal", models.DecimalField(decimal_places=2, default=0, max_digits=14)),
                ("discount_total", models.DecimalField(decimal_places=2, default=0, max_digits=14)),
                ("shipping_fee", models.DecimalField(decimal_places=2, default=0, max_digits=14)),
                ("grand_total", models.DecimalField(decimal_places=2, default=0, max_digits=14)),
                ("shipping_address", models.JSONField(default=dict)),
                ("idempotency_key", models.CharField(max_length=128, unique=True)),
                ("metadata", models.JSONField(blank=True, default=dict)),
            ],
            options={
                "db_table": "orders",
                "indexes": [
                    models.Index(fields=["customer_id", "status"], name="idx_orders_customer_status"),
                    models.Index(fields=["idempotency_key"], name="idx_orders_idempotency"),
                    models.Index(fields=["created_at"], name="idx_orders_created_at"),
                ],
            },
        ),
        migrations.CreateModel(
            name="OrderLine",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("product_id", models.UUIDField()),
                ("sku", models.CharField(max_length=64)),
                ("product_name", models.CharField(max_length=255)),
                ("quantity", models.PositiveIntegerField()),
                ("unit_price", models.DecimalField(decimal_places=2, max_digits=14)),
                ("line_total", models.DecimalField(decimal_places=2, max_digits=14)),
                ("attributes_snapshot", models.JSONField(blank=True, default=dict)),
                ("order", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="lines", to="orders.order")),
            ],
            options={
                "db_table": "order_lines",
                "indexes": [
                    models.Index(fields=["order"], name="idx_order_lines_order"),
                    models.Index(fields=["sku"], name="idx_order_lines_sku"),
                ],
            },
        ),
        migrations.CreateModel(
            name="OrderStatusHistory",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("from_status", models.CharField(max_length=32)),
                ("to_status", models.CharField(max_length=32)),
                ("actor_id", models.UUIDField(blank=True, null=True)),
                ("note", models.TextField(blank=True)),
                ("order", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="status_history", to="orders.order")),
            ],
            options={
                "db_table": "order_status_history",
                "indexes": [models.Index(fields=["order", "created_at"], name="idx_order_status_history")],
            },
        ),
    ]
