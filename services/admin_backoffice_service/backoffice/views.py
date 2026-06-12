from rest_framework import viewsets

from ecommerce_common.permissions import IsAdminOrStaff

from .models import AuditLog, BackofficeWorkItem
from .serializers import AuditLogSerializer, BackofficeWorkItemSerializer


class BackofficePermissionMixin:
    permission_classes = [IsAdminOrStaff]


class BackofficeWorkItemViewSet(BackofficePermissionMixin, viewsets.ModelViewSet):
    queryset = BackofficeWorkItem.objects.all().order_by("-created_at")
    serializer_class = BackofficeWorkItemSerializer


class AuditLogViewSet(BackofficePermissionMixin, viewsets.ModelViewSet):
    queryset = AuditLog.objects.all().order_by("-created_at")
    serializer_class = AuditLogSerializer

    def perform_create(self, serializer):
        user = self.request.user
        serializer.save(actor_id=getattr(user, "id", None), actor_role=getattr(user, "role", ""))
