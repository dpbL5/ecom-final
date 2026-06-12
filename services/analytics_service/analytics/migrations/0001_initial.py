import uuid

from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="AnalyticsEvent",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("event_name", models.CharField(max_length=128)),
                ("aggregate_type", models.CharField(blank=True, max_length=64)),
                ("aggregate_id", models.UUIDField(blank=True, null=True)),
                ("customer_id", models.UUIDField(blank=True, null=True)),
                ("payload", models.JSONField(blank=True, default=dict)),
                ("occurred_at", models.DateTimeField()),
            ],
            options={
                "db_table": "analytics_events",
                "indexes": [
                    models.Index(fields=["event_name", "occurred_at"], name="idx_analytics_event_time"),
                    models.Index(fields=["customer_id"], name="idx_analytics_customer"),
                ],
            },
        ),
        migrations.CreateModel(
            name="DailySalesMetric",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("metric_date", models.DateField(unique=True)),
                ("order_count", models.PositiveIntegerField(default=0)),
                ("gross_revenue", models.DecimalField(decimal_places=2, default=0, max_digits=16)),
                ("net_revenue", models.DecimalField(decimal_places=2, default=0, max_digits=16)),
                ("currency", models.CharField(default="VND", max_length=3)),
            ],
            options={"db_table": "daily_sales_metrics"},
        ),
    ]
