from django.db import models

from ecommerce_common.models import TimeStampedModel, UUIDPrimaryKeyModel


class ProductInteraction(UUIDPrimaryKeyModel, TimeStampedModel):
    class EventType(models.TextChoices):
        VIEWED = "viewed", "Viewed"
        ADDED_TO_CART = "added_to_cart", "Added to cart"
        PURCHASED = "purchased", "Purchased"
        WISHLISTED = "wishlisted", "Wishlisted"

    customer_id = models.UUIDField()
    product_id = models.UUIDField()
    sku = models.CharField(max_length=64)
    event_type = models.CharField(max_length=32, choices=EventType.choices)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table = "product_interactions"
        indexes = [
            models.Index(fields=["customer_id", "event_type"], name="idx_pi_customer_event"),
            models.Index(fields=["product_id"], name="idx_pi_product"),
        ]


class Recommendation(UUIDPrimaryKeyModel, TimeStampedModel):
    customer_id = models.UUIDField()
    product_id = models.UUIDField()
    sku = models.CharField(max_length=64)
    score = models.DecimalField(max_digits=8, decimal_places=4, default=0)
    reason = models.CharField(max_length=255, blank=True)

    class Meta:
        db_table = "recommendations"
        constraints = [
            models.UniqueConstraint(fields=["customer_id", "product_id"], name="uq_rec_customer_product"),
        ]
        indexes = [models.Index(fields=["customer_id", "-score"], name="idx_rec_customer")]
