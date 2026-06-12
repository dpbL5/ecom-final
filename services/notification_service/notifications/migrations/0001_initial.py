import uuid

from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="NotificationTemplate",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("code", models.CharField(max_length=64, unique=True)),
                ("channel", models.CharField(max_length=32)),
                ("subject", models.CharField(blank=True, max_length=255)),
                ("body", models.TextField()),
                ("is_active", models.BooleanField(default=True)),
            ],
            options={"db_table": "notification_templates"},
        ),
        migrations.CreateModel(
            name="Notification",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("recipient_user_id", models.UUIDField(blank=True, null=True)),
                ("recipient", models.CharField(max_length=255)),
                ("channel", models.CharField(max_length=32)),
                ("template_code", models.CharField(blank=True, max_length=64)),
                ("subject", models.CharField(blank=True, max_length=255)),
                ("body", models.TextField()),
                ("payload", models.JSONField(blank=True, default=dict)),
                ("status", models.CharField(choices=[("queued", "Queued"), ("sent", "Sent"), ("failed", "Failed")], default="queued", max_length=32)),
                ("error_message", models.TextField(blank=True)),
            ],
            options={
                "db_table": "notifications",
                "indexes": [
                    models.Index(fields=["recipient_user_id"], name="idx_notifications_user"),
                    models.Index(fields=["status", "created_at"], name="idx_notifications_status"),
                ],
            },
        ),
    ]
