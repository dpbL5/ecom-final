from decimal import Decimal

from rest_framework import serializers

from .models import Coupon, PriceBook, ProductPrice, PromotionCampaign


class PriceBookSerializer(serializers.ModelSerializer):
    class Meta:
        model = PriceBook
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")


class ProductPriceSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductPrice
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")


class PromotionCampaignSerializer(serializers.ModelSerializer):
    class Meta:
        model = PromotionCampaign
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")


class CouponSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coupon
        fields = "__all__"
        read_only_fields = ("id", "redeemed_count", "created_at", "updated_at")


class QuoteItemSerializer(serializers.Serializer):
    sku = serializers.CharField(max_length=64)
    quantity = serializers.IntegerField(min_value=1)


class QuoteRequestSerializer(serializers.Serializer):
    items = QuoteItemSerializer(many=True)
    coupon_code = serializers.CharField(max_length=64, required=False, allow_blank=True)


class QuoteResponseSerializer(serializers.Serializer):
    currency = serializers.CharField()
    subtotal = serializers.DecimalField(max_digits=14, decimal_places=2)
    discount_total = serializers.DecimalField(max_digits=14, decimal_places=2)
    total = serializers.DecimalField(max_digits=14, decimal_places=2)
    items = serializers.ListField()


def calculate_discount(amount, coupon):
    if not coupon:
        return Decimal("0.00")
    percent = coupon.campaign.discount_percent / Decimal("100")
    return (amount * percent).quantize(Decimal("0.01"))
