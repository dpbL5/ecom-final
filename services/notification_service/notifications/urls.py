from rest_framework.routers import DefaultRouter

from .views import NotificationTemplateViewSet, NotificationViewSet


router = DefaultRouter()
router.register("templates", NotificationTemplateViewSet)
router.register("notifications", NotificationViewSet, basename="notification")

urlpatterns = router.urls
