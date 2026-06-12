from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import CouponViewSet, PriceBookViewSet, ProductPriceViewSet, PromotionCampaignViewSet, QuoteView


router = DefaultRouter()
router.register("price-books", PriceBookViewSet)
router.register("prices", ProductPriceViewSet)
router.register("promotions", PromotionCampaignViewSet)
router.register("coupons", CouponViewSet)

urlpatterns = [
    path("quote/", QuoteView.as_view(), name="quote"),
] + router.urls
