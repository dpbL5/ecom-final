import uuid

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Cart",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("customer_id", models.UUIDField(blank=True, null=True)),
                ("session_key", models.CharField(blank=True, max_length=128)),
                ("status", models.CharField(choices=[("active", "Active"), ("checked_out", "Checked out"), ("abandoned", "Abandoned")], default="active", max_length=32)),
            ],
            options={
                "db_table": "carts",
                "indexes": [
                    models.Index(fields=["customer_id", "status"], name="idx_carts_customer_status"),
                    models.Index(fields=["session_key"], name="idx_carts_session_key"),
                ],
            },
        ),
        migrations.CreateModel(
            name="CartItem",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("product_id", models.UUIDField()),
                ("sku", models.CharField(max_length=64)),
                ("product_name", models.CharField(max_length=255)),
                ("quantity", models.PositiveIntegerField()),
                ("unit_price_snapshot", models.DecimalField(blank=True, decimal_places=2, max_digits=14, null=True)),
                ("attributes_snapshot", models.JSONField(blank=True, default=dict)),
                ("cart", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="items", to="carts.cart")),
            ],
            options={
                "db_table": "cart_items",
                "indexes": [
                    models.Index(fields=["cart"], name="idx_cart_items_cart"),
                    models.Index(fields=["sku"], name="idx_cart_items_sku"),
                ],
                "constraints": [
                    models.UniqueConstraint(fields=("cart", "sku"), name="uq_cart_item_sku"),
                ],
            },
        ),
    ]
