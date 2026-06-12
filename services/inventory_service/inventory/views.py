from django.db import transaction
from rest_framework import status, views, viewsets
from rest_framework.response import Response

from .models import StockItem, StockReservation, Warehouse
from .serializers import ReserveStockSerializer, StockItemSerializer, StockReservationSerializer, WarehouseSerializer


class WarehouseViewSet(viewsets.ModelViewSet):
    queryset = Warehouse.objects.all().order_by("code")
    serializer_class = WarehouseSerializer


class StockItemViewSet(viewsets.ModelViewSet):
    queryset = StockItem.objects.select_related("warehouse").all().order_by("sku")
    serializer_class = StockItemSerializer


class StockReservationViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = StockReservation.objects.select_related("stock_item").all().order_by("-created_at")
    serializer_class = StockReservationSerializer


class ReserveStockView(views.APIView):
    def post(self, request):
        serializer = ReserveStockSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        # Neu request retry voi cung idempotency_key, tra lai reservation cu thay vi giu them hang.
        existing = StockReservation.objects.filter(idempotency_key=data["idempotency_key"]).first()
        if existing:
            return Response(StockReservationSerializer(existing).data)

        # atomic + select_for_update khoa dong stock trong luc tinh available_quantity de tranh overselling.
        with transaction.atomic():
            queryset = StockItem.objects.select_for_update().filter(sku=data["sku"])
            if data.get("warehouse_id"):
                queryset = queryset.filter(warehouse_id=data["warehouse_id"])
            stock_item = queryset.order_by("created_at").first()
            if not stock_item:
                return Response({"detail": "Stock item not found."}, status=status.HTTP_404_NOT_FOUND)
            if stock_item.available_quantity < data["quantity"]:
                return Response({"detail": "Insufficient stock."}, status=status.HTTP_409_CONFLICT)

            stock_item.quantity_reserved += data["quantity"]
            stock_item.version += 1
            # Chi tang reserved, chua tru on_hand. Viec tru hang that su co the lam khi fulfill/ship.
            stock_item.save(update_fields=["quantity_reserved", "version", "updated_at"])
            reservation = StockReservation.objects.create(
                stock_item=stock_item,
                order_id=data["order_id"],
                quantity=data["quantity"],
                idempotency_key=data["idempotency_key"],
            )

        return Response(StockReservationSerializer(reservation).data, status=status.HTTP_201_CREATED)
