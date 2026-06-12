from django.db import models

from ecommerce_common.models import TimeStampedModel, UUIDPrimaryKeyModel


class ProductReview(UUIDPrimaryKeyModel, TimeStampedModel):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        APPROVED = "approved", "Approved"
        REJECTED = "rejected", "Rejected"

    product_id = models.UUIDField()
    customer_id = models.UUIDField()
    order_id = models.UUIDField()
    rating = models.PositiveSmallIntegerField()
    title = models.CharField(max_length=255, blank=True)
    body = models.TextField(blank=True)
    status = models.CharField(max_length=32, choices=Status.choices, default=Status.PENDING)

    class Meta:
        db_table = "product_reviews"
        constraints = [
            models.UniqueConstraint(fields=["product_id", "customer_id", "order_id"], name="uq_review_purchase"),
            models.CheckConstraint(check=models.Q(rating__gte=1) & models.Q(rating__lte=5), name="ck_review_rating_1_5"),
        ]
        indexes = [
            models.Index(fields=["product_id", "status"], name="idx_reviews_product_status"),
            models.Index(fields=["customer_id"], name="idx_reviews_customer"),
        ]
