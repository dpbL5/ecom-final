from rest_framework import serializers

from .models import AuditLog, BackofficeWorkItem


class BackofficeWorkItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = BackofficeWorkItem
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")


class AuditLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuditLog
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")
