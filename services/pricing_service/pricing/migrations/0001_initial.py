import uuid

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="PriceBook",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("code", models.CharField(max_length=64, unique=True)),
                ("name", models.CharField(max_length=255)),
                ("currency", models.CharField(default="VND", max_length=3)),
                ("is_active", models.BooleanField(default=True)),
            ],
            options={"db_table": "price_books"},
        ),
        migrations.CreateModel(
            name="PromotionCampaign",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("code", models.CharField(max_length=64, unique=True)),
                ("name", models.CharField(max_length=255)),
                ("discount_percent", models.DecimalField(decimal_places=2, default=0, max_digits=5)),
                ("is_active", models.BooleanField(default=True)),
                ("starts_at", models.DateTimeField(blank=True, null=True)),
                ("ends_at", models.DateTimeField(blank=True, null=True)),
            ],
            options={"db_table": "promotion_campaigns"},
        ),
        migrations.CreateModel(
            name="ProductPrice",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("product_id", models.UUIDField()),
                ("sku", models.CharField(max_length=64)),
                ("amount", models.DecimalField(decimal_places=2, max_digits=14)),
                ("compare_at_amount", models.DecimalField(blank=True, decimal_places=2, max_digits=14, null=True)),
                ("starts_at", models.DateTimeField(blank=True, null=True)),
                ("ends_at", models.DateTimeField(blank=True, null=True)),
                ("is_active", models.BooleanField(default=True)),
                ("price_book", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="prices", to="pricing.pricebook")),
            ],
            options={
                "db_table": "product_prices",
                "indexes": [
                    models.Index(fields=["sku", "is_active"], name="idx_prices_sku_active"),
                    models.Index(fields=["product_id"], name="idx_prices_product_id"),
                ],
            },
        ),
        migrations.CreateModel(
            name="Coupon",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("code", models.CharField(max_length=64, unique=True)),
                ("max_redemptions", models.PositiveIntegerField(default=1)),
                ("redeemed_count", models.PositiveIntegerField(default=0)),
                ("is_active", models.BooleanField(default=True)),
                ("campaign", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="coupons", to="pricing.promotioncampaign")),
            ],
            options={"db_table": "coupons"},
        ),
    ]
