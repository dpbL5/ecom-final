from rest_framework import serializers

from .models import Order, OrderLine, OrderStatusHistory


class OrderLineSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderLine
        fields = "__all__"
        read_only_fields = ("id", "order", "created_at", "updated_at")


class OrderStatusHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderStatusHistory
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")


class OrderSerializer(serializers.ModelSerializer):
    # lines duoc gui kem khi tao order; status_history chi doc de frontend/admin xem lich su.
    lines = OrderLineSerializer(many=True)
    status_history = OrderStatusHistorySerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = "__all__"
        read_only_fields = ("id", "status", "created_at", "updated_at", "status_history")

    def create(self, validated_data):
        # Tao order cha truoc, sau do tao cac dong hang con tro ve order do.
        lines = validated_data.pop("lines", [])
        order = Order.objects.create(**validated_data)
        for line in lines:
            OrderLine.objects.create(order=order, **line)
        OrderStatusHistory.objects.create(order=order, from_status="", to_status=order.status, note="Order created")
        return order
