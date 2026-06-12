import uuid

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Category",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(max_length=255)),
                ("slug", models.SlugField(max_length=255, unique=True)),
                ("is_active", models.BooleanField(default=True)),
                ("parent", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="children", to="catalog.category")),
            ],
            options={
                "db_table": "categories",
                "indexes": [models.Index(fields=["slug"], name="idx_categories_slug")],
            },
        ),
        migrations.CreateModel(
            name="Product",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("sku", models.CharField(max_length=64, unique=True)),
                ("name", models.CharField(max_length=255)),
                ("slug", models.SlugField(max_length=255, unique=True)),
                ("description", models.TextField(blank=True)),
                ("brand", models.CharField(blank=True, max_length=128)),
                ("product_type", models.CharField(choices=[("book", "Book"), ("electronics", "Electronics"), ("fashion", "Fashion")], max_length=32)),
                ("status", models.CharField(choices=[("draft", "Draft"), ("published", "Published"), ("archived", "Archived")], default="draft", max_length=32)),
                ("attributes", models.JSONField(blank=True, default=dict)),
                ("image_urls", models.JSONField(blank=True, default=list)),
                ("created_by", models.UUIDField(blank=True, null=True)),
                ("category", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="products", to="catalog.category")),
            ],
            options={
                "db_table": "products",
                "indexes": [
                    models.Index(fields=["sku"], name="idx_products_sku"),
                    models.Index(fields=["slug"], name="idx_products_slug"),
                    models.Index(fields=["product_type", "status"], name="idx_products_type_status"),
                ],
            },
        ),
        migrations.CreateModel(
            name="ProductVariant",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("sku", models.CharField(max_length=64, unique=True)),
                ("name", models.CharField(blank=True, max_length=255)),
                ("attributes", models.JSONField(blank=True, default=dict)),
                ("is_active", models.BooleanField(default=True)),
                ("product", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="variants", to="catalog.product")),
            ],
            options={
                "db_table": "product_variants",
                "indexes": [
                    models.Index(fields=["sku"], name="idx_product_variants_sku"),
                    models.Index(fields=["product", "is_active"], name="idx_variants_product_active"),
                ],
            },
        ),
    ]
