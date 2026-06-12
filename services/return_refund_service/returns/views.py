from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import RefundRequest, ReturnRequest
from .serializers import RefundRequestSerializer, ReturnRequestSerializer


class ReturnRequestViewSet(viewsets.ModelViewSet):
    serializer_class = ReturnRequestSerializer
    queryset = ReturnRequest.objects.prefetch_related("items", "refund_requests").all().order_by("-created_at")

    def get_queryset(self):
        user = self.request.user
        queryset = super().get_queryset()
        if getattr(user, "role", None) == "customer":
            return queryset.filter(customer_id=user.id)
        return queryset

    @action(detail=True, methods=["post"])
    def approve(self, request, pk=None):
        return self._set_status(ReturnRequest.Status.APPROVED)

    @action(detail=True, methods=["post"])
    def reject(self, request, pk=None):
        return self._set_status(ReturnRequest.Status.REJECTED)

    @action(detail=True, methods=["post"])
    def receive(self, request, pk=None):
        return self._set_status(ReturnRequest.Status.RECEIVED)

    def _set_status(self, target_status):
        return_request = self.get_object()
        return_request.status = target_status
        return_request.save(update_fields=["status", "updated_at"])
        return Response(self.get_serializer(return_request).data)


class RefundRequestViewSet(viewsets.ModelViewSet):
    serializer_class = RefundRequestSerializer
    queryset = RefundRequest.objects.select_related("return_request").all().order_by("-created_at")
