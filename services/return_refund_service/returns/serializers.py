from rest_framework import serializers

from .models import RefundRequest, ReturnItem, ReturnRequest


class ReturnItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReturnItem
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")


class RefundRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = RefundRequest
        fields = "__all__"
        read_only_fields = ("id", "status", "created_at", "updated_at")


class ReturnRequestSerializer(serializers.ModelSerializer):
    items = ReturnItemSerializer(many=True)
    refund_requests = RefundRequestSerializer(many=True, read_only=True)

    class Meta:
        model = ReturnRequest
        fields = "__all__"
        read_only_fields = ("id", "status", "created_at", "updated_at", "refund_requests")

    def create(self, validated_data):
        items = validated_data.pop("items", [])
        return_request = ReturnRequest.objects.create(**validated_data)
        for item in items:
            ReturnItem.objects.create(return_request=return_request, **item)
        return return_request
