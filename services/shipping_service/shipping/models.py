from django.db import models

from ecommerce_common.models import TimeStampedModel, UUIDPrimaryKeyModel


class Carrier(UUIDPrimaryKeyModel, TimeStampedModel):
    code = models.CharField(max_length=64, unique=True)
    name = models.CharField(max_length=255)
    tracking_url_template = models.CharField(max_length=512, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "carriers"


class Shipment(UUIDPrimaryKeyModel, TimeStampedModel):
    class Status(models.TextChoices):
        CREATED = "created", "Created"
        PICKED_UP = "picked_up", "Picked up"
        IN_TRANSIT = "in_transit", "In transit"
        DELIVERED = "delivered", "Delivered"
        FAILED = "failed", "Failed"

    order_id = models.UUIDField()
    carrier = models.ForeignKey(Carrier, related_name="shipments", on_delete=models.PROTECT)
    tracking_number = models.CharField(max_length=128, blank=True)
    status = models.CharField(max_length=32, choices=Status.choices, default=Status.CREATED)
    ship_to = models.JSONField(default=dict)
    package_items = models.JSONField(default=list)

    class Meta:
        db_table = "shipments"
        indexes = [
            models.Index(fields=["order_id"], name="idx_shipments_order_id"),
            models.Index(fields=["tracking_number"], name="idx_shipments_tracking"),
        ]


class DeliveryEvent(UUIDPrimaryKeyModel, TimeStampedModel):
    shipment = models.ForeignKey(Shipment, related_name="events", on_delete=models.CASCADE)
    status = models.CharField(max_length=32)
    location = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    raw_payload = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table = "delivery_events"
        indexes = [models.Index(fields=["shipment", "created_at"], name="idx_delivery_events")]
