import uuid

from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="ProductInteraction",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("customer_id", models.UUIDField()),
                ("product_id", models.UUIDField()),
                ("sku", models.CharField(max_length=64)),
                ("event_type", models.CharField(choices=[("viewed", "Viewed"), ("added_to_cart", "Added to cart"), ("purchased", "Purchased"), ("wishlisted", "Wishlisted")], max_length=32)),
                ("metadata", models.JSONField(blank=True, default=dict)),
            ],
            options={
                "db_table": "product_interactions",
                "indexes": [
                    models.Index(fields=["customer_id", "event_type"], name="idx_pi_customer_event"),
                    models.Index(fields=["product_id"], name="idx_pi_product"),
                ],
            },
        ),
        migrations.CreateModel(
            name="Recommendation",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("customer_id", models.UUIDField()),
                ("product_id", models.UUIDField()),
                ("sku", models.CharField(max_length=64)),
                ("score", models.DecimalField(decimal_places=4, default=0, max_digits=8)),
                ("reason", models.CharField(blank=True, max_length=255)),
            ],
            options={
                "db_table": "recommendations",
                "indexes": [models.Index(fields=["customer_id", "-score"], name="idx_rec_customer")],
                "constraints": [
                    models.UniqueConstraint(fields=("customer_id", "product_id"), name="uq_rec_customer_product"),
                ],
            },
        ),
    ]
