from django.db import models

from ecommerce_common.models import TimeStampedModel, UUIDPrimaryKeyModel


class BackofficeWorkItem(UUIDPrimaryKeyModel, TimeStampedModel):
    class Status(models.TextChoices):
        OPEN = "open", "Open"
        IN_PROGRESS = "in_progress", "In progress"
        RESOLVED = "resolved", "Resolved"
        CLOSED = "closed", "Closed"

    context = models.CharField(max_length=64)
    aggregate_type = models.CharField(max_length=64)
    aggregate_id = models.UUIDField(null=True, blank=True)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    assigned_to = models.UUIDField(null=True, blank=True)
    status = models.CharField(max_length=32, choices=Status.choices, default=Status.OPEN)
    priority = models.PositiveSmallIntegerField(default=3)

    class Meta:
        db_table = "backoffice_work_items"
        indexes = [
            models.Index(fields=["context", "status"], name="idx_work_items_context_status"),
            models.Index(fields=["assigned_to", "status"], name="idx_work_items_assignee"),
        ]


class AuditLog(UUIDPrimaryKeyModel, TimeStampedModel):
    actor_id = models.UUIDField(null=True, blank=True)
    actor_role = models.CharField(max_length=32, blank=True)
    action = models.CharField(max_length=128)
    context = models.CharField(max_length=64)
    aggregate_type = models.CharField(max_length=64, blank=True)
    aggregate_id = models.UUIDField(null=True, blank=True)
    before = models.JSONField(default=dict, blank=True)
    after = models.JSONField(default=dict, blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table = "audit_logs"
        indexes = [
            models.Index(fields=["actor_id", "created_at"], name="idx_audit_actor_time"),
            models.Index(fields=["context", "created_at"], name="idx_audit_context_time"),
        ]
