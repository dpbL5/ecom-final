from rest_framework import serializers

from .models import ProductInteraction, Recommendation


class ProductInteractionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductInteraction
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")


class RecommendationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recommendation
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")


class AIChatRequestSerializer(serializers.Serializer):
    message = serializers.CharField(max_length=500)
    customer_id = serializers.CharField(required=False, allow_blank=True)


class AIProductSuggestionSerializer(serializers.Serializer):
    product_id = serializers.UUIDField()
    sku = serializers.CharField()
    name = serializers.CharField()
    product_type = serializers.CharField()
    brand = serializers.CharField(allow_blank=True)
    reason = serializers.CharField()
    score = serializers.FloatField(required=False)
    source = serializers.CharField(required=False)


class AIChatResponseSerializer(serializers.Serializer):
    answer = serializers.CharField()
    source = serializers.CharField()
    intent = serializers.CharField(allow_blank=True)
    suggestions = AIProductSuggestionSerializer(many=True)


class NextBuyRecommendationSerializer(serializers.Serializer):
    product_id = serializers.CharField()
    sku = serializers.CharField()
    name = serializers.CharField(allow_blank=True)
    product_type = serializers.CharField(allow_blank=True)
    brand = serializers.CharField(allow_blank=True)
    score = serializers.FloatField()
    source = serializers.CharField()
    reason = serializers.CharField()


class NextBuyRecommendationResponseSerializer(serializers.Serializer):
    customer_id = serializers.CharField()
    source = serializers.CharField()
    model = serializers.DictField()
    recommendations = NextBuyRecommendationSerializer(many=True)
