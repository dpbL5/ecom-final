from django.db import models

from ecommerce_common.models import TimeStampedModel, UUIDPrimaryKeyModel


class CustomerProfile(UUIDPrimaryKeyModel, TimeStampedModel):
    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        BLOCKED = "blocked", "Blocked"

    user_id = models.UUIDField(unique=True)
    email = models.EmailField()
    full_name = models.CharField(max_length=255)
    phone = models.CharField(max_length=32, blank=True)
    status = models.CharField(max_length=32, choices=Status.choices, default=Status.ACTIVE)
    preferences = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table = "customer_profiles"
        indexes = [
            models.Index(fields=["user_id"], name="idx_customer_user_id"),
            models.Index(fields=["email"], name="idx_customer_email"),
        ]

    def __str__(self):
        return self.email


class Address(UUIDPrimaryKeyModel, TimeStampedModel):
    customer = models.ForeignKey(CustomerProfile, related_name="addresses", on_delete=models.CASCADE)
    label = models.CharField(max_length=64, blank=True)
    recipient_name = models.CharField(max_length=255)
    phone = models.CharField(max_length=32)
    line1 = models.CharField(max_length=255)
    line2 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=128)
    state = models.CharField(max_length=128, blank=True)
    country = models.CharField(max_length=2, default="VN")
    postal_code = models.CharField(max_length=32, blank=True)
    is_default = models.BooleanField(default=False)

    class Meta:
        db_table = "customer_addresses"
        indexes = [
            models.Index(fields=["customer", "is_default"], name="idx_address_default"),
        ]


class WishlistItem(UUIDPrimaryKeyModel, TimeStampedModel):
    customer = models.ForeignKey(CustomerProfile, related_name="wishlist_items", on_delete=models.CASCADE)
    product_id = models.UUIDField()
    sku = models.CharField(max_length=64)
    name_snapshot = models.CharField(max_length=255, blank=True)

    class Meta:
        db_table = "wishlist_items"
        constraints = [
            models.UniqueConstraint(fields=["customer", "product_id"], name="uq_wishlist_customer_product"),
        ]
        indexes = [
            models.Index(fields=["product_id"], name="idx_wishlist_product_id"),
            models.Index(fields=["sku"], name="idx_wishlist_sku"),
        ]
