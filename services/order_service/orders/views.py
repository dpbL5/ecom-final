from django.db import IntegrityError
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Order
from .serializers import OrderSerializer


class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    queryset = Order.objects.prefetch_related("lines", "status_history").all().order_by("-created_at")

    def get_queryset(self):
        user = self.request.user
        queryset = super().get_queryset()
        # Customer chi duoc doc don cua minh; staff/admin xem duoc tat ca don.
        if getattr(user, "role", None) == "customer":
            return queryset.filter(customer_id=user.id)
        return queryset

    def create(self, request, *args, **kwargs):
        # Idempotency key giup frontend/service retry tao order ma khong tao trung don.
        key = request.data.get("idempotency_key")
        if key:
            existing = Order.objects.filter(idempotency_key=key).first()
            if existing:
                return Response(self.get_serializer(existing).data)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            self.perform_create(serializer)
        except IntegrityError:
            existing = Order.objects.get(idempotency_key=key)
            return Response(self.get_serializer(existing).data)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    @action(detail=True, methods=["post"], url_path="mark-paid")
    def mark_paid(self, request, pk=None):
        return self._transition(pk, Order.Status.PAID, request)

    @action(detail=True, methods=["post"])
    def confirm(self, request, pk=None):
        return self._transition(pk, Order.Status.CONFIRMED, request)

    @action(detail=True, methods=["post"])
    def cancel(self, request, pk=None):
        return self._transition(pk, Order.Status.CANCELLED, request)

    @action(detail=True, methods=["post"])
    def ship(self, request, pk=None):
        return self._transition(pk, Order.Status.SHIPPED, request)

    @action(detail=True, methods=["post"])
    def complete(self, request, pk=None):
        return self._transition(pk, Order.Status.COMPLETED, request)

    def _transition(self, pk, target_status, request):
        order = self.get_object()
        try:
            # Rule chuyen trang thai nam trong model Order de moi action dung chung mot nguon logic.
            order.transition_to(target_status, actor_id=getattr(request.user, "id", None), note=request.data.get("note", ""))
        except ValueError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_409_CONFLICT)
        return Response(self.get_serializer(order).data)
