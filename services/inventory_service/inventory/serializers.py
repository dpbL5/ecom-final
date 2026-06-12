from rest_framework import serializers

from .models import StockItem, StockReservation, Warehouse


class WarehouseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Warehouse
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")


class StockItemSerializer(serializers.ModelSerializer):
    available_quantity = serializers.IntegerField(read_only=True)

    class Meta:
        model = StockItem
        fields = "__all__"
        read_only_fields = ("id", "quantity_reserved", "version", "created_at", "updated_at", "available_quantity")


class StockReservationSerializer(serializers.ModelSerializer):
    class Meta:
        model = StockReservation
        fields = "__all__"
        read_only_fields = ("id", "status", "created_at", "updated_at")


class ReserveStockSerializer(serializers.Serializer):
    sku = serializers.CharField(max_length=64)
    warehouse_id = serializers.UUIDField(required=False)
    order_id = serializers.UUIDField()
    quantity = serializers.IntegerField(min_value=1)
    idempotency_key = serializers.CharField(max_length=128)
