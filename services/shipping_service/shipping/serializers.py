from rest_framework import serializers

from .models import Carrier, DeliveryEvent, Shipment


class CarrierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Carrier
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")


class DeliveryEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeliveryEvent
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")


class ShipmentSerializer(serializers.ModelSerializer):
    events = DeliveryEventSerializer(many=True, read_only=True)

    class Meta:
        model = Shipment
        fields = "__all__"
        read_only_fields = ("id", "status", "created_at", "updated_at", "events")


class ShipmentStatusSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=Shipment.Status.choices)
    location = serializers.CharField(max_length=255, required=False, allow_blank=True)
    description = serializers.CharField(required=False, allow_blank=True)
    raw_payload = serializers.JSONField(required=False)
