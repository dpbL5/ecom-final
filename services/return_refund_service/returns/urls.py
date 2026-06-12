from rest_framework.routers import DefaultRouter

from .views import RefundRequestViewSet, ReturnRequestViewSet


router = DefaultRouter()
router.register("returns", ReturnRequestViewSet, basename="return")
router.register("refund-requests", RefundRequestViewSet, basename="refund-request")

urlpatterns = router.urls
