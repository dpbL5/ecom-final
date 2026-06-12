from rest_framework.routers import DefaultRouter

from .views import AddressViewSet, CustomerProfileViewSet, WishlistItemViewSet


router = DefaultRouter()
router.register("customers", CustomerProfileViewSet, basename="customer")
router.register("addresses", AddressViewSet, basename="address")
router.register("wishlist", WishlistItemViewSet, basename="wishlist")

urlpatterns = router.urls
