import uuid

from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="SearchProductDocument",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("product_id", models.UUIDField(unique=True)),
                ("sku", models.CharField(max_length=64)),
                ("name", models.CharField(max_length=255)),
                ("description", models.TextField(blank=True)),
                ("product_type", models.CharField(max_length=32)),
                ("category_id", models.UUIDField(blank=True, null=True)),
                ("brand", models.CharField(blank=True, max_length=128)),
                ("status", models.CharField(default="published", max_length=32)),
                ("price_amount", models.DecimalField(blank=True, decimal_places=2, max_digits=14, null=True)),
                ("currency", models.CharField(default="VND", max_length=3)),
                ("available_quantity", models.IntegerField(default=0)),
                ("rating_average", models.DecimalField(blank=True, decimal_places=2, max_digits=3, null=True)),
                ("attributes", models.JSONField(blank=True, default=dict)),
                ("search_text", models.TextField(blank=True)),
            ],
            options={
                "db_table": "search_product_documents",
                "indexes": [
                    models.Index(fields=["sku"], name="idx_search_sku"),
                    models.Index(fields=["product_type", "status"], name="idx_search_type_status"),
                    models.Index(fields=["brand"], name="idx_search_brand"),
                ],
            },
        ),
    ]
