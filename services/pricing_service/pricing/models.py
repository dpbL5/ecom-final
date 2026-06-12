from django.db import models

from ecommerce_common.models import TimeStampedModel, UUIDPrimaryKeyModel


class PriceBook(UUIDPrimaryKeyModel, TimeStampedModel):
    code = models.CharField(max_length=64, unique=True)
    name = models.CharField(max_length=255)
    currency = models.CharField(max_length=3, default="VND")
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "price_books"


class ProductPrice(UUIDPrimaryKeyModel, TimeStampedModel):
    price_book = models.ForeignKey(PriceBook, related_name="prices", on_delete=models.PROTECT)
    product_id = models.UUIDField()
    sku = models.CharField(max_length=64)
    amount = models.DecimalField(max_digits=14, decimal_places=2)
    compare_at_amount = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    starts_at = models.DateTimeField(null=True, blank=True)
    ends_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "product_prices"
        indexes = [
            models.Index(fields=["sku", "is_active"], name="idx_prices_sku_active"),
            models.Index(fields=["product_id"], name="idx_prices_product_id"),
        ]


class PromotionCampaign(UUIDPrimaryKeyModel, TimeStampedModel):
    code = models.CharField(max_length=64, unique=True)
    name = models.CharField(max_length=255)
    discount_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)
    starts_at = models.DateTimeField(null=True, blank=True)
    ends_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "promotion_campaigns"


class Coupon(UUIDPrimaryKeyModel, TimeStampedModel):
    code = models.CharField(max_length=64, unique=True)
    campaign = models.ForeignKey(PromotionCampaign, related_name="coupons", on_delete=models.PROTECT)
    max_redemptions = models.PositiveIntegerField(default=1)
    redeemed_count = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "coupons"
