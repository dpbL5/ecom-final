import uuid

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="ReturnRequest",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("order_id", models.UUIDField()),
                ("customer_id", models.UUIDField()),
                ("reason", models.TextField()),
                ("status", models.CharField(choices=[("requested", "Requested"), ("approved", "Approved"), ("rejected", "Rejected"), ("received", "Received"), ("closed", "Closed")], default="requested", max_length=32)),
                ("idempotency_key", models.CharField(max_length=128, unique=True)),
            ],
            options={
                "db_table": "return_requests",
                "indexes": [
                    models.Index(fields=["order_id"], name="idx_returns_order_id"),
                    models.Index(fields=["customer_id", "status"], name="idx_returns_customer_status"),
                ],
            },
        ),
        migrations.CreateModel(
            name="ReturnItem",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("order_line_id", models.UUIDField()),
                ("product_id", models.UUIDField()),
                ("sku", models.CharField(max_length=64)),
                ("quantity", models.PositiveIntegerField()),
                ("reason", models.TextField(blank=True)),
                ("return_request", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="items", to="returns.returnrequest")),
            ],
            options={"db_table": "return_items"},
        ),
        migrations.CreateModel(
            name="RefundRequest",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("payment_id", models.UUIDField(blank=True, null=True)),
                ("amount", models.DecimalField(decimal_places=2, max_digits=14)),
                ("status", models.CharField(choices=[("requested", "Requested"), ("sent_to_payment", "Sent to payment"), ("completed", "Completed"), ("failed", "Failed")], default="requested", max_length=32)),
                ("idempotency_key", models.CharField(max_length=128, unique=True)),
                ("return_request", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="refund_requests", to="returns.returnrequest")),
            ],
            options={
                "db_table": "refund_requests",
                "indexes": [models.Index(fields=["idempotency_key"], name="idx_refund_req_idem")],
            },
        ),
    ]
