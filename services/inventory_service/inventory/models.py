from django.db import models

from ecommerce_common.models import TimeStampedModel, UUIDPrimaryKeyModel


class Warehouse(UUIDPrimaryKeyModel, TimeStampedModel):
    code = models.CharField(max_length=64, unique=True)
    name = models.CharField(max_length=255)
    city = models.CharField(max_length=128, blank=True)
    country = models.CharField(max_length=2, default="VN")
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "warehouses"

    def __str__(self):
        return self.code


class StockItem(UUIDPrimaryKeyModel, TimeStampedModel):
    warehouse = models.ForeignKey(Warehouse, related_name="stock_items", on_delete=models.PROTECT)
    product_id = models.UUIDField()
    sku = models.CharField(max_length=64)
    quantity_on_hand = models.PositiveIntegerField(default=0)
    quantity_reserved = models.PositiveIntegerField(default=0)
    version = models.PositiveIntegerField(default=1)

    class Meta:
        db_table = "stock_items"
        constraints = [
            models.UniqueConstraint(fields=["warehouse", "sku"], name="uq_stock_warehouse_sku"),
            models.CheckConstraint(check=models.Q(quantity_on_hand__gte=models.F("quantity_reserved")), name="ck_stock_reserved_lte_on_hand"),
        ]
        indexes = [
            models.Index(fields=["sku"], name="idx_stock_items_sku"),
            models.Index(fields=["product_id"], name="idx_stock_items_product_id"),
        ]

    @property
    def available_quantity(self):
        return self.quantity_on_hand - self.quantity_reserved


class StockReservation(UUIDPrimaryKeyModel, TimeStampedModel):
    class Status(models.TextChoices):
        RESERVED = "reserved", "Reserved"
        RELEASED = "released", "Released"
        DEDUCTED = "deducted", "Deducted"

    stock_item = models.ForeignKey(StockItem, related_name="reservations", on_delete=models.PROTECT)
    order_id = models.UUIDField()
    idempotency_key = models.CharField(max_length=128, unique=True)
    quantity = models.PositiveIntegerField()
    status = models.CharField(max_length=32, choices=Status.choices, default=Status.RESERVED)

    class Meta:
        db_table = "stock_reservations"
        indexes = [
            models.Index(fields=["order_id"], name="idx_reservations_order_id"),
            models.Index(fields=["idempotency_key"], name="idx_reservations_idempotency"),
        ]
