from django.db import models

from ecommerce_common.models import TimeStampedModel, UUIDPrimaryKeyModel


class Category(UUIDPrimaryKeyModel, TimeStampedModel):
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    parent = models.ForeignKey("self", null=True, blank=True, related_name="children", on_delete=models.PROTECT)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "categories"
        indexes = [models.Index(fields=["slug"], name="idx_categories_slug")]

    def __str__(self):
        return self.name


class Product(UUIDPrimaryKeyModel, TimeStampedModel):
    class ProductType(models.TextChoices):
        BOOK = "book", "Book"
        ELECTRONICS = "electronics", "Electronics"
        FASHION = "fashion", "Fashion"

    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        PUBLISHED = "published", "Published"
        ARCHIVED = "archived", "Archived"

    category = models.ForeignKey(Category, related_name="products", on_delete=models.PROTECT)
    sku = models.CharField(max_length=64, unique=True)
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    description = models.TextField(blank=True)
    brand = models.CharField(max_length=128, blank=True)
    product_type = models.CharField(max_length=32, choices=ProductType.choices)
    status = models.CharField(max_length=32, choices=Status.choices, default=Status.DRAFT)
    attributes = models.JSONField(default=dict, blank=True)
    image_urls = models.JSONField(default=list, blank=True)
    created_by = models.UUIDField(null=True, blank=True)

    class Meta:
        db_table = "products"
        indexes = [
            models.Index(fields=["sku"], name="idx_products_sku"),
            models.Index(fields=["slug"], name="idx_products_slug"),
            models.Index(fields=["product_type", "status"], name="idx_products_type_status"),
        ]

    def __str__(self):
        return self.name


class ProductVariant(UUIDPrimaryKeyModel, TimeStampedModel):
    product = models.ForeignKey(Product, related_name="variants", on_delete=models.CASCADE)
    sku = models.CharField(max_length=64, unique=True)
    name = models.CharField(max_length=255, blank=True)
    attributes = models.JSONField(default=dict, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "product_variants"
        indexes = [
            models.Index(fields=["sku"], name="idx_product_variants_sku"),
            models.Index(fields=["product", "is_active"], name="idx_variants_product_active"),
        ]

    def __str__(self):
        return self.sku
