from rest_framework import viewsets

from .models import AnalyticsEvent, DailySalesMetric
from .serializers import AnalyticsEventSerializer, DailySalesMetricSerializer


class AnalyticsEventViewSet(viewsets.ModelViewSet):
    queryset = AnalyticsEvent.objects.all().order_by("-occurred_at")
    serializer_class = AnalyticsEventSerializer


class DailySalesMetricViewSet(viewsets.ModelViewSet):
    queryset = DailySalesMetric.objects.all().order_by("-metric_date")
    serializer_class = DailySalesMetricSerializer
