from django.conf import settings
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from ecommerce_common.clients import ServiceClient, ServiceClientError, bearer_token_from_request

from .models import Carrier, DeliveryEvent, Shipment
from .serializers import CarrierSerializer, ShipmentSerializer, ShipmentStatusSerializer


class CarrierViewSet(viewsets.ModelViewSet):
    queryset = Carrier.objects.all().order_by("code")
    serializer_class = CarrierSerializer


class ShipmentViewSet(viewsets.ModelViewSet):
    serializer_class = ShipmentSerializer
    queryset = Shipment.objects.select_related("carrier").prefetch_related("events").all().order_by("-created_at")

    @action(detail=True, methods=["post"], url_path="update-status")
    def update_status(self, request, pk=None):
        shipment = self.get_object()
        serializer = ShipmentStatusSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        shipment.status = data["status"]
        shipment.save(update_fields=["status", "updated_at"])
        # Luu delivery event rieng de giu lich su tung lan hang thay doi trang thai/vi tri.
        DeliveryEvent.objects.create(
            shipment=shipment,
            status=data["status"],
            location=data.get("location", ""),
            description=data.get("description", ""),
            raw_payload=data.get("raw_payload", {}),
        )

        token = bearer_token_from_request(request)
        if token and data["status"] in {Shipment.Status.IN_TRANSIT, Shipment.Status.DELIVERED}:
            action = "ship" if data["status"] == Shipment.Status.IN_TRANSIT else "complete"
            try:
                # Shipping status anh huong order status, nen service nay goi order-service action tuong ung.
                ServiceClient(settings.SERVICE_URLS["order"]).request(
                    "POST",
                    f"/api/v1/orders/{shipment.order_id}/{action}/",
                    token=token,
                    json={"note": f"Shipment {data['status']}"},
                )
            except ServiceClientError as exc:
                return Response({"detail": str(exc)}, status=status.HTTP_502_BAD_GATEWAY)

        return Response(self.get_serializer(shipment).data)
