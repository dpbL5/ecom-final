from django.db import models

from ecommerce_common.models import TimeStampedModel, UUIDPrimaryKeyModel


class NotificationTemplate(UUIDPrimaryKeyModel, TimeStampedModel):
    code = models.CharField(max_length=64, unique=True)
    channel = models.CharField(max_length=32)
    subject = models.CharField(max_length=255, blank=True)
    body = models.TextField()
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "notification_templates"


class Notification(UUIDPrimaryKeyModel, TimeStampedModel):
    class Status(models.TextChoices):
        QUEUED = "queued", "Queued"
        SENT = "sent", "Sent"
        FAILED = "failed", "Failed"

    recipient_user_id = models.UUIDField(null=True, blank=True)
    recipient = models.CharField(max_length=255)
    channel = models.CharField(max_length=32)
    template_code = models.CharField(max_length=64, blank=True)
    subject = models.CharField(max_length=255, blank=True)
    body = models.TextField()
    payload = models.JSONField(default=dict, blank=True)
    status = models.CharField(max_length=32, choices=Status.choices, default=Status.QUEUED)
    error_message = models.TextField(blank=True)

    class Meta:
        db_table = "notifications"
        indexes = [
            models.Index(fields=["recipient_user_id"], name="idx_notifications_user"),
            models.Index(fields=["status", "created_at"], name="idx_notifications_status"),
        ]
