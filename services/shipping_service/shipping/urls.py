from rest_framework.routers import DefaultRouter

from .views import CarrierViewSet, ShipmentViewSet


router = DefaultRouter()
router.register("carriers", CarrierViewSet)
router.register("shipments", ShipmentViewSet, basename="shipment")

urlpatterns = router.urls
