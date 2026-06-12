from rest_framework import serializers

from .models import AnalyticsEvent, DailySalesMetric


class AnalyticsEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnalyticsEvent
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")


class DailySalesMetricSerializer(serializers.ModelSerializer):
    class Meta:
        model = DailySalesMetric
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")
