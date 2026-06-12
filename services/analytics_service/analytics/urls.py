from rest_framework.routers import DefaultRouter

from .views import AnalyticsEventViewSet, DailySalesMetricViewSet


router = DefaultRouter()
router.register("events", AnalyticsEventViewSet)
router.register("daily-sales", DailySalesMetricViewSet)

urlpatterns = router.urls
