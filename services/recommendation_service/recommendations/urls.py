from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import (
    AIChatbotView,
    GraphRecommendationView,
    GraphSeedView,
    NextBuyRecommendationView,
    ProductInteractionViewSet,
    RecommendationForCustomerView,
    RecommendationViewSet,
)


router = DefaultRouter()
router.register("interactions", ProductInteractionViewSet)
router.register("recommendations", RecommendationViewSet)

urlpatterns = [
    path("recommendations/for-customer/<uuid:customer_id>/", RecommendationForCustomerView.as_view(), name="recommendations-for-customer"),
    path("recommendations/next-buy/<uuid:customer_id>/", NextBuyRecommendationView.as_view(), name="recommendations-next-buy"),
    path("graph/recommendations/<str:customer_id>/", GraphRecommendationView.as_view(), name="graph-recommendations"),
    path("graph/seed/", GraphSeedView.as_view(), name="graph-seed"),
    path("ai/chatbot/", AIChatbotView.as_view(), name="ai-chatbot"),
] + router.urls
