from rest_framework.routers import DefaultRouter

from .views import PaymentViewSet, RefundViewSet


router = DefaultRouter()
router.register("payments", PaymentViewSet, basename="payment")
router.register("refunds", RefundViewSet, basename="refund")

urlpatterns = router.urls
