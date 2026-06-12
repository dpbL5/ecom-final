from django.db import models

from ecommerce_common.models import TimeStampedModel, UUIDPrimaryKeyModel


class Cart(UUIDPrimaryKeyModel, TimeStampedModel):
    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        CHECKED_OUT = "checked_out", "Checked out"
        ABANDONED = "abandoned", "Abandoned"

    customer_id = models.UUIDField(null=True, blank=True)
    session_key = models.CharField(max_length=128, blank=True)
    status = models.CharField(max_length=32, choices=Status.choices, default=Status.ACTIVE)

    class Meta:
        db_table = "carts"
        indexes = [
            models.Index(fields=["customer_id", "status"], name="idx_carts_customer_status"),
            models.Index(fields=["session_key"], name="idx_carts_session_key"),
        ]


class CartItem(UUIDPrimaryKeyModel, TimeStampedModel):
    cart = models.ForeignKey(Cart, related_name="items", on_delete=models.CASCADE)
    product_id = models.UUIDField()
    sku = models.CharField(max_length=64)
    product_name = models.CharField(max_length=255)
    quantity = models.PositiveIntegerField()
    unit_price_snapshot = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    attributes_snapshot = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table = "cart_items"
        constraints = [
            models.UniqueConstraint(fields=["cart", "sku"], name="uq_cart_item_sku"),
        ]
        indexes = [
            models.Index(fields=["cart"], name="idx_cart_items_cart"),
            models.Index(fields=["sku"], name="idx_cart_items_sku"),
        ]
