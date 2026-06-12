import uuid

from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="BackofficeWorkItem",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("context", models.CharField(max_length=64)),
                ("aggregate_type", models.CharField(max_length=64)),
                ("aggregate_id", models.UUIDField(blank=True, null=True)),
                ("title", models.CharField(max_length=255)),
                ("description", models.TextField(blank=True)),
                ("assigned_to", models.UUIDField(blank=True, null=True)),
                ("status", models.CharField(choices=[("open", "Open"), ("in_progress", "In progress"), ("resolved", "Resolved"), ("closed", "Closed")], default="open", max_length=32)),
                ("priority", models.PositiveSmallIntegerField(default=3)),
            ],
            options={
                "db_table": "backoffice_work_items",
                "indexes": [
                    models.Index(fields=["context", "status"], name="idx_work_items_context_status"),
                    models.Index(fields=["assigned_to", "status"], name="idx_work_items_assignee"),
                ],
            },
        ),
        migrations.CreateModel(
            name="AuditLog",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("actor_id", models.UUIDField(blank=True, null=True)),
                ("actor_role", models.CharField(blank=True, max_length=32)),
                ("action", models.CharField(max_length=128)),
                ("context", models.CharField(max_length=64)),
                ("aggregate_type", models.CharField(blank=True, max_length=64)),
                ("aggregate_id", models.UUIDField(blank=True, null=True)),
                ("before", models.JSONField(blank=True, default=dict)),
                ("after", models.JSONField(blank=True, default=dict)),
                ("metadata", models.JSONField(blank=True, default=dict)),
            ],
            options={
                "db_table": "audit_logs",
                "indexes": [
                    models.Index(fields=["actor_id", "created_at"], name="idx_audit_actor_time"),
                    models.Index(fields=["context", "created_at"], name="idx_audit_context_time"),
                ],
            },
        ),
    ]
