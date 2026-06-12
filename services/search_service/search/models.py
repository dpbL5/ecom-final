from django.db import models

from ecommerce_common.models import TimeStampedModel, UUIDPrimaryKeyModel


class SearchProductDocument(UUIDPrimaryKeyModel, TimeStampedModel):
    product_id = models.UUIDField(unique=True)
    sku = models.CharField(max_length=64)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    product_type = models.CharField(max_length=32)
    category_id = models.UUIDField(null=True, blank=True)
    brand = models.CharField(max_length=128, blank=True)
    status = models.CharField(max_length=32, default="published")
    price_amount = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    currency = models.CharField(max_length=3, default="VND")
    available_quantity = models.IntegerField(default=0)
    rating_average = models.DecimalField(max_digits=3, decimal_places=2, null=True, blank=True)
    attributes = models.JSONField(default=dict, blank=True)
    image_urls = models.JSONField(default=list, blank=True)
    search_text = models.TextField(blank=True)

    class Meta:
        db_table = "search_product_documents"
        indexes = [
            models.Index(fields=["sku"], name="idx_search_sku"),
            models.Index(fields=["product_type", "status"], name="idx_search_type_status"),
            models.Index(fields=["brand"], name="idx_search_brand"),
        ]
