from django.urls import include, path

from ecommerce_common.views import HealthView

urlpatterns = [
    path("health/", HealthView.as_view(), name="health"),
    path("api/v1/", include("shipping.urls")),
]
