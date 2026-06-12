from django.conf import settings
from django.db import IntegrityError
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from ecommerce_common.clients import ServiceClient, ServiceClientError, bearer_token_from_request

from .models import Payment, PaymentTransaction, Refund
from .serializers import PaymentResultSerializer, PaymentSerializer, RefundSerializer


class PaymentViewSet(viewsets.ModelViewSet):
    serializer_class = PaymentSerializer
    queryset = Payment.objects.prefetch_related("transactions", "refunds").all().order_by("-created_at")

    def get_queryset(self):
        user = self.request.user
        queryset = super().get_queryset()
        if getattr(user, "role", None) == "customer":
            return queryset.filter(customer_id=user.id)
        return queryset

    def create(self, request, *args, **kwargs):
        # Tao payment co idempotency de retry tu frontend/cong thanh toan khong tao trung payment.
        key = request.data.get("idempotency_key")
        if key:
            existing = Payment.objects.filter(idempotency_key=key).first()
            if existing:
                return Response(self.get_serializer(existing).data)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            self.perform_create(serializer)
        except IntegrityError:
            existing = Payment.objects.get(idempotency_key=key)
            return Response(self.get_serializer(existing).data)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"], url_path="mark-succeeded")
    def mark_succeeded(self, request, pk=None):
        return self._apply_result(request, Payment.Status.SUCCEEDED)

    @action(detail=True, methods=["post"], url_path="mark-failed")
    def mark_failed(self, request, pk=None):
        return self._apply_result(request, Payment.Status.FAILED)

    def _apply_result(self, request, target_status):
        payment = self.get_object()
        serializer = PaymentResultSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        # provider_transaction_id unique de mot giao dich tu cong thanh toan chi duoc ghi mot lan.
        PaymentTransaction.objects.get_or_create(
            provider_transaction_id=data["provider_transaction_id"],
            defaults={
                "payment": payment,
                "status": target_status,
                "payload": data.get("payload", {}),
            },
        )
        payment.status = target_status
        payment.save(update_fields=["status", "updated_at"])

        if target_status == Payment.Status.SUCCEEDED:
            token = bearer_token_from_request(request)
            if token:
                try:
                    # Khi thanh toan thanh cong, payment-service bao order-service chuyen order sang paid.
                    ServiceClient(settings.SERVICE_URLS["order"]).request(
                        "POST",
                        f"/api/v1/orders/{payment.order_id}/mark-paid/",
                        token=token,
                        json={"note": "Payment succeeded"},
                    )
                except ServiceClientError as exc:
                    return Response({"detail": str(exc)}, status=status.HTTP_502_BAD_GATEWAY)
        return Response(self.get_serializer(payment).data)


class RefundViewSet(viewsets.ModelViewSet):
    serializer_class = RefundSerializer
    queryset = Refund.objects.select_related("payment").all().order_by("-created_at")

    def create(self, request, *args, **kwargs):
        key = request.data.get("idempotency_key")
        if key:
            existing = Refund.objects.filter(idempotency_key=key).first()
            if existing:
                return Response(self.get_serializer(existing).data)
        return super().create(request, *args, **kwargs)
