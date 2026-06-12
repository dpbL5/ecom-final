import uuid

from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="ProductReview",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("product_id", models.UUIDField()),
                ("customer_id", models.UUIDField()),
                ("order_id", models.UUIDField()),
                ("rating", models.PositiveSmallIntegerField()),
                ("title", models.CharField(blank=True, max_length=255)),
                ("body", models.TextField(blank=True)),
                ("status", models.CharField(choices=[("pending", "Pending"), ("approved", "Approved"), ("rejected", "Rejected")], default="pending", max_length=32)),
            ],
            options={
                "db_table": "product_reviews",
                "indexes": [
                    models.Index(fields=["product_id", "status"], name="idx_reviews_product_status"),
                    models.Index(fields=["customer_id"], name="idx_reviews_customer"),
                ],
                "constraints": [
                    models.UniqueConstraint(fields=("product_id", "customer_id", "order_id"), name="uq_review_purchase"),
                    models.CheckConstraint(check=models.Q(rating__gte=1) & models.Q(rating__lte=5), name="ck_review_rating_1_5"),
                ],
            },
        ),
    ]
