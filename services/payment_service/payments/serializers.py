from rest_framework import serializers

from .models import Payment, PaymentTransaction, Refund


class PaymentTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentTransaction
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")


class RefundSerializer(serializers.ModelSerializer):
    class Meta:
        model = Refund
        fields = "__all__"
        read_only_fields = ("id", "status", "created_at", "updated_at")


class PaymentSerializer(serializers.ModelSerializer):
    transactions = PaymentTransactionSerializer(many=True, read_only=True)
    refunds = RefundSerializer(many=True, read_only=True)

    class Meta:
        model = Payment
        fields = "__all__"
        read_only_fields = ("id", "status", "created_at", "updated_at", "transactions", "refunds")


class PaymentResultSerializer(serializers.Serializer):
    provider_transaction_id = serializers.CharField(max_length=128)
    payload = serializers.JSONField(required=False)
