import uuid

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="CustomerProfile",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("user_id", models.UUIDField(unique=True)),
                ("email", models.EmailField(max_length=254)),
                ("full_name", models.CharField(max_length=255)),
                ("phone", models.CharField(blank=True, max_length=32)),
                ("status", models.CharField(choices=[("active", "Active"), ("blocked", "Blocked")], default="active", max_length=32)),
                ("preferences", models.JSONField(blank=True, default=dict)),
            ],
            options={
                "db_table": "customer_profiles",
                "indexes": [
                    models.Index(fields=["user_id"], name="idx_customer_user_id"),
                    models.Index(fields=["email"], name="idx_customer_email"),
                ],
            },
        ),
        migrations.CreateModel(
            name="Address",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("label", models.CharField(blank=True, max_length=64)),
                ("recipient_name", models.CharField(max_length=255)),
                ("phone", models.CharField(max_length=32)),
                ("line1", models.CharField(max_length=255)),
                ("line2", models.CharField(blank=True, max_length=255)),
                ("city", models.CharField(max_length=128)),
                ("state", models.CharField(blank=True, max_length=128)),
                ("country", models.CharField(default="VN", max_length=2)),
                ("postal_code", models.CharField(blank=True, max_length=32)),
                ("is_default", models.BooleanField(default=False)),
                ("customer", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="addresses", to="customers.customerprofile")),
            ],
            options={
                "db_table": "customer_addresses",
                "indexes": [models.Index(fields=["customer", "is_default"], name="idx_address_default")],
            },
        ),
        migrations.CreateModel(
            name="WishlistItem",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("product_id", models.UUIDField()),
                ("sku", models.CharField(max_length=64)),
                ("name_snapshot", models.CharField(blank=True, max_length=255)),
                ("customer", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="wishlist_items", to="customers.customerprofile")),
            ],
            options={
                "db_table": "wishlist_items",
                "indexes": [
                    models.Index(fields=["product_id"], name="idx_wishlist_product_id"),
                    models.Index(fields=["sku"], name="idx_wishlist_sku"),
                ],
                "constraints": [
                    models.UniqueConstraint(fields=("customer", "product_id"), name="uq_wishlist_customer_product"),
                ],
            },
        ),
    ]
