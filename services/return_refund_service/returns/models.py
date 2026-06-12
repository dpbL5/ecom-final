from django.db import models

from ecommerce_common.models import TimeStampedModel, UUIDPrimaryKeyModel


class ReturnRequest(UUIDPrimaryKeyModel, TimeStampedModel):
    class Status(models.TextChoices):
        REQUESTED = "requested", "Requested"
        APPROVED = "approved", "Approved"
        REJECTED = "rejected", "Rejected"
        RECEIVED = "received", "Received"
        CLOSED = "closed", "Closed"

    order_id = models.UUIDField()
    customer_id = models.UUIDField()
    reason = models.TextField()
    status = models.CharField(max_length=32, choices=Status.choices, default=Status.REQUESTED)
    idempotency_key = models.CharField(max_length=128, unique=True)

    class Meta:
        db_table = "return_requests"
        indexes = [
            models.Index(fields=["order_id"], name="idx_returns_order_id"),
            models.Index(fields=["customer_id", "status"], name="idx_returns_customer_status"),
        ]


class ReturnItem(UUIDPrimaryKeyModel, TimeStampedModel):
    return_request = models.ForeignKey(ReturnRequest, related_name="items", on_delete=models.CASCADE)
    order_line_id = models.UUIDField()
    product_id = models.UUIDField()
    sku = models.CharField(max_length=64)
    quantity = models.PositiveIntegerField()
    reason = models.TextField(blank=True)

    class Meta:
        db_table = "return_items"


class RefundRequest(UUIDPrimaryKeyModel, TimeStampedModel):
    class Status(models.TextChoices):
        REQUESTED = "requested", "Requested"
        SENT_TO_PAYMENT = "sent_to_payment", "Sent to payment"
        COMPLETED = "completed", "Completed"
        FAILED = "failed", "Failed"

    return_request = models.ForeignKey(ReturnRequest, related_name="refund_requests", on_delete=models.PROTECT)
    payment_id = models.UUIDField(null=True, blank=True)
    amount = models.DecimalField(max_digits=14, decimal_places=2)
    status = models.CharField(max_length=32, choices=Status.choices, default=Status.REQUESTED)
    idempotency_key = models.CharField(max_length=128, unique=True)

    class Meta:
        db_table = "refund_requests"
        indexes = [models.Index(fields=["idempotency_key"], name="idx_refund_req_idem")]
