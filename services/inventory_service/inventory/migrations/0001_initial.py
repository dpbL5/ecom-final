import uuid

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Warehouse",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("code", models.CharField(max_length=64, unique=True)),
                ("name", models.CharField(max_length=255)),
                ("city", models.CharField(blank=True, max_length=128)),
                ("country", models.CharField(default="VN", max_length=2)),
                ("is_active", models.BooleanField(default=True)),
            ],
            options={"db_table": "warehouses"},
        ),
        migrations.CreateModel(
            name="StockItem",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("product_id", models.UUIDField()),
                ("sku", models.CharField(max_length=64)),
                ("quantity_on_hand", models.PositiveIntegerField(default=0)),
                ("quantity_reserved", models.PositiveIntegerField(default=0)),
                ("version", models.PositiveIntegerField(default=1)),
                ("warehouse", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="stock_items", to="inventory.warehouse")),
            ],
            options={
                "db_table": "stock_items",
                "indexes": [
                    models.Index(fields=["sku"], name="idx_stock_items_sku"),
                    models.Index(fields=["product_id"], name="idx_stock_items_product_id"),
                ],
                "constraints": [
                    models.UniqueConstraint(fields=("warehouse", "sku"), name="uq_stock_warehouse_sku"),
                    models.CheckConstraint(check=models.Q(quantity_on_hand__gte=models.F("quantity_reserved")), name="ck_stock_reserved_lte_on_hand"),
                ],
            },
        ),
        migrations.CreateModel(
            name="StockReservation",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("order_id", models.UUIDField()),
                ("idempotency_key", models.CharField(max_length=128, unique=True)),
                ("quantity", models.PositiveIntegerField()),
                ("status", models.CharField(choices=[("reserved", "Reserved"), ("released", "Released"), ("deducted", "Deducted")], default="reserved", max_length=32)),
                ("stock_item", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="reservations", to="inventory.stockitem")),
            ],
            options={
                "db_table": "stock_reservations",
                "indexes": [
                    models.Index(fields=["order_id"], name="idx_reservations_order_id"),
                    models.Index(fields=["idempotency_key"], name="idx_reservations_idempotency"),
                ],
            },
        ),
    ]
