from django.db import models

from ecommerce_common.models import TimeStampedModel, UUIDPrimaryKeyModel


class AnalyticsEvent(UUIDPrimaryKeyModel, TimeStampedModel):
    event_name = models.CharField(max_length=128)
    aggregate_type = models.CharField(max_length=64, blank=True)
    aggregate_id = models.UUIDField(null=True, blank=True)
    customer_id = models.UUIDField(null=True, blank=True)
    payload = models.JSONField(default=dict, blank=True)
    occurred_at = models.DateTimeField()

    class Meta:
        db_table = "analytics_events"
        indexes = [
            models.Index(fields=["event_name", "occurred_at"], name="idx_analytics_event_time"),
            models.Index(fields=["customer_id"], name="idx_analytics_customer"),
        ]


class DailySalesMetric(UUIDPrimaryKeyModel, TimeStampedModel):
    metric_date = models.DateField(unique=True)
    order_count = models.PositiveIntegerField(default=0)
    gross_revenue = models.DecimalField(max_digits=16, decimal_places=2, default=0)
    net_revenue = models.DecimalField(max_digits=16, decimal_places=2, default=0)
    currency = models.CharField(max_length=3, default="VND")

    class Meta:
        db_table = "daily_sales_metrics"
