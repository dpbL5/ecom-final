from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import ProductDocumentViewSet, SearchView


router = DefaultRouter()
router.register("documents", ProductDocumentViewSet, basename="search-document")

urlpatterns = [
    path("products/search/", SearchView.as_view(), name="product-search"),
] + router.urls
