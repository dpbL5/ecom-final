import uuid

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Carrier",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("code", models.CharField(max_length=64, unique=True)),
                ("name", models.CharField(max_length=255)),
                ("tracking_url_template", models.CharField(blank=True, max_length=512)),
                ("is_active", models.BooleanField(default=True)),
            ],
            options={"db_table": "carriers"},
        ),
        migrations.CreateModel(
            name="Shipment",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("order_id", models.UUIDField()),
                ("tracking_number", models.CharField(blank=True, max_length=128)),
                ("status", models.CharField(choices=[("created", "Created"), ("picked_up", "Picked up"), ("in_transit", "In transit"), ("delivered", "Delivered"), ("failed", "Failed")], default="created", max_length=32)),
                ("ship_to", models.JSONField(default=dict)),
                ("package_items", models.JSONField(default=list)),
                ("carrier", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="shipments", to="shipping.carrier")),
            ],
            options={
                "db_table": "shipments",
                "indexes": [
                    models.Index(fields=["order_id"], name="idx_shipments_order_id"),
                    models.Index(fields=["tracking_number"], name="idx_shipments_tracking"),
                ],
            },
        ),
        migrations.CreateModel(
            name="DeliveryEvent",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("status", models.CharField(max_length=32)),
                ("location", models.CharField(blank=True, max_length=255)),
                ("description", models.TextField(blank=True)),
                ("raw_payload", models.JSONField(blank=True, default=dict)),
                ("shipment", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="events", to="shipping.shipment")),
            ],
            options={
                "db_table": "delivery_events",
                "indexes": [models.Index(fields=["shipment", "created_at"], name="idx_delivery_events")],
            },
        ),
    ]
