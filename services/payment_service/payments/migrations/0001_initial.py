import uuid

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Payment",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("order_id", models.UUIDField()),
                ("customer_id", models.UUIDField()),
                ("amount", models.DecimalField(decimal_places=2, max_digits=14)),
                ("currency", models.CharField(default="VND", max_length=3)),
                ("provider", models.CharField(default="mock", max_length=64)),
                ("provider_reference", models.CharField(blank=True, max_length=128)),
                ("idempotency_key", models.CharField(max_length=128, unique=True)),
                ("status", models.CharField(choices=[("requested", "Requested"), ("succeeded", "Succeeded"), ("failed", "Failed"), ("refunded", "Refunded")], default="requested", max_length=32)),
                ("metadata", models.JSONField(blank=True, default=dict)),
            ],
            options={
                "db_table": "payments",
                "indexes": [
                    models.Index(fields=["order_id"], name="idx_payments_order_id"),
                    models.Index(fields=["customer_id"], name="idx_payments_customer_id"),
                    models.Index(fields=["idempotency_key"], name="idx_payments_idempotency"),
                ],
            },
        ),
        migrations.CreateModel(
            name="PaymentTransaction",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("provider_transaction_id", models.CharField(max_length=128, unique=True)),
                ("status", models.CharField(max_length=32)),
                ("payload", models.JSONField(blank=True, default=dict)),
                ("payment", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="transactions", to="payments.payment")),
            ],
            options={
                "db_table": "payment_transactions",
                "indexes": [models.Index(fields=["provider_transaction_id"], name="idx_transactions_provider")],
            },
        ),
        migrations.CreateModel(
            name="Refund",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("amount", models.DecimalField(decimal_places=2, max_digits=14)),
                ("reason", models.TextField(blank=True)),
                ("status", models.CharField(choices=[("requested", "Requested"), ("succeeded", "Succeeded"), ("failed", "Failed")], default="requested", max_length=32)),
                ("idempotency_key", models.CharField(max_length=128, unique=True)),
                ("payment", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="refunds", to="payments.payment")),
            ],
            options={
                "db_table": "refunds",
                "indexes": [models.Index(fields=["idempotency_key"], name="idx_refunds_idempotency")],
            },
        ),
    ]
