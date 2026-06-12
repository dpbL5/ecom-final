from rest_framework.routers import DefaultRouter

from .views import AuditLogViewSet, BackofficeWorkItemViewSet


router = DefaultRouter()
router.register("work-items", BackofficeWorkItemViewSet)
router.register("audit-logs", AuditLogViewSet)

urlpatterns = router.urls
