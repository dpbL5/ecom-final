from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Notification, NotificationTemplate
from .serializers import NotificationSerializer, NotificationTemplateSerializer


class NotificationTemplateViewSet(viewsets.ModelViewSet):
    queryset = NotificationTemplate.objects.all().order_by("code")
    serializer_class = NotificationTemplateSerializer


class NotificationViewSet(viewsets.ModelViewSet):
    queryset = Notification.objects.all().order_by("-created_at")
    serializer_class = NotificationSerializer

    @action(detail=True, methods=["post"])
    def send(self, request, pk=None):
        notification = self.get_object()
        notification.status = Notification.Status.SENT
        notification.error_message = ""
        notification.save(update_fields=["status", "error_message", "updated_at"])
        return Response(self.get_serializer(notification).data)
