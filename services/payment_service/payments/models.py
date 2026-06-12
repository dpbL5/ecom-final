from django.db import models

from ecommerce_common.models import TimeStampedModel, UUIDPrimaryKeyModel


class Payment(UUIDPrimaryKeyModel, TimeStampedModel):
    class Status(models.TextChoices):
        REQUESTED = "requested", "Requested"
        SUCCEEDED = "succeeded", "Succeeded"
        FAILED = "failed", "Failed"
        REFUNDED = "refunded", "Refunded"

    order_id = models.UUIDField()
    customer_id = models.UUIDField()
    amount = models.DecimalField(max_digits=14, decimal_places=2)
    currency = models.CharField(max_length=3, default="VND")
    provider = models.CharField(max_length=64, default="mock")
    provider_reference = models.CharField(max_length=128, blank=True)
    idempotency_key = models.CharField(max_length=128, unique=True)
    status = models.CharField(max_length=32, choices=Status.choices, default=Status.REQUESTED)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table = "payments"
        indexes = [
            models.Index(fields=["order_id"], name="idx_payments_order_id"),
            models.Index(fields=["customer_id"], name="idx_payments_customer_id"),
            models.Index(fields=["idempotency_key"], name="idx_payments_idempotency"),
        ]


class PaymentTransaction(UUIDPrimaryKeyModel, TimeStampedModel):
    payment = models.ForeignKey(Payment, related_name="transactions", on_delete=models.CASCADE)
    provider_transaction_id = models.CharField(max_length=128, unique=True)
    status = models.CharField(max_length=32)
    payload = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table = "payment_transactions"
        indexes = [models.Index(fields=["provider_transaction_id"], name="idx_transactions_provider")]


class Refund(UUIDPrimaryKeyModel, TimeStampedModel):
    class Status(models.TextChoices):
        REQUESTED = "requested", "Requested"
        SUCCEEDED = "succeeded", "Succeeded"
        FAILED = "failed", "Failed"

    payment = models.ForeignKey(Payment, related_name="refunds", on_delete=models.PROTECT)
    amount = models.DecimalField(max_digits=14, decimal_places=2)
    reason = models.TextField(blank=True)
    status = models.CharField(max_length=32, choices=Status.choices, default=Status.REQUESTED)
    idempotency_key = models.CharField(max_length=128, unique=True)

    class Meta:
        db_table = "refunds"
        indexes = [models.Index(fields=["idempotency_key"], name="idx_refunds_idempotency")]
