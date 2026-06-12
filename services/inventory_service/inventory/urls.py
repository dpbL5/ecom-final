from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import ReserveStockView, StockItemViewSet, StockReservationViewSet, WarehouseViewSet


router = DefaultRouter()
router.register("warehouses", WarehouseViewSet)
router.register("stock-items", StockItemViewSet)
router.register("reservations", StockReservationViewSet)

urlpatterns = [
    path("stock/reserve/", ReserveStockView.as_view(), name="stock-reserve"),
] + router.urls
