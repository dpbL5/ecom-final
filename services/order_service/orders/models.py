from django.db import models

from ecommerce_common.models import TimeStampedModel, UUIDPrimaryKeyModel


class Order(UUIDPrimaryKeyModel, TimeStampedModel):
    class Status(models.TextChoices):
        PENDING_PAYMENT = "pending_payment", "Pending payment"
        PAID = "paid", "Paid"
        CONFIRMED = "confirmed", "Confirmed"
        PACKED = "packed", "Packed"
        SHIPPED = "shipped", "Shipped"
        COMPLETED = "completed", "Completed"
        CANCELLED = "cancelled", "Cancelled"
        REFUNDED = "refunded", "Refunded"

    customer_id = models.UUIDField()
    status = models.CharField(max_length=32, choices=Status.choices, default=Status.PENDING_PAYMENT)
    currency = models.CharField(max_length=3, default="VND")
    subtotal = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    discount_total = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    shipping_fee = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    grand_total = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    shipping_address = models.JSONField(default=dict)
    idempotency_key = models.CharField(max_length=128, unique=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table = "orders"
        indexes = [
            models.Index(fields=["customer_id", "status"], name="idx_orders_customer_status"),
            models.Index(fields=["idempotency_key"], name="idx_orders_idempotency"),
            models.Index(fields=["created_at"], name="idx_orders_created_at"),
        ]

    def transition_to(self, status, actor_id=None, note=""):
        if self.status == status:
            return
        # Bang trang thai hop le cua don hang. Neu chuyen sai thu tu se bi chan bang ValueError.
        allowed = {
            self.Status.PENDING_PAYMENT: {self.Status.PAID, self.Status.CANCELLED},
            self.Status.PAID: {self.Status.CONFIRMED, self.Status.CANCELLED, self.Status.REFUNDED},
            self.Status.CONFIRMED: {self.Status.PACKED, self.Status.SHIPPED, self.Status.CANCELLED},
            self.Status.PACKED: {self.Status.SHIPPED},
            self.Status.SHIPPED: {self.Status.COMPLETED},
            self.Status.COMPLETED: {self.Status.REFUNDED},
            self.Status.CANCELLED: set(),
            self.Status.REFUNDED: set(),
        }
        if status not in allowed[self.status]:
            raise ValueError(f"Cannot transition order from {self.status} to {status}.")
        previous_status = self.status
        self.status = status
        self.save(update_fields=["status", "updated_at"])
        # Moi lan doi trang thai deu ghi lich su de admin/debug biet ai da doi va doi vi ly do gi.
        OrderStatusHistory.objects.create(
            order=self,
            from_status=previous_status,
            to_status=status,
            actor_id=actor_id,
            note=note,
        )


class OrderLine(UUIDPrimaryKeyModel, TimeStampedModel):
    order = models.ForeignKey(Order, related_name="lines", on_delete=models.CASCADE)
    product_id = models.UUIDField()
    sku = models.CharField(max_length=64)
    product_name = models.CharField(max_length=255)
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=14, decimal_places=2)
    line_total = models.DecimalField(max_digits=14, decimal_places=2)
    attributes_snapshot = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table = "order_lines"
        indexes = [
            models.Index(fields=["order"], name="idx_order_lines_order"),
            models.Index(fields=["sku"], name="idx_order_lines_sku"),
        ]


class OrderStatusHistory(UUIDPrimaryKeyModel, TimeStampedModel):
    order = models.ForeignKey(Order, related_name="status_history", on_delete=models.CASCADE)
    from_status = models.CharField(max_length=32)
    to_status = models.CharField(max_length=32)
    actor_id = models.UUIDField(null=True, blank=True)
    note = models.TextField(blank=True)

    class Meta:
        db_table = "order_status_history"
        indexes = [models.Index(fields=["order", "created_at"], name="idx_order_status_history")]
