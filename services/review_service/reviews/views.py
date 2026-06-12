from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import ProductReview
from .serializers import ProductReviewSerializer


class ProductReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ProductReviewSerializer
    queryset = ProductReview.objects.all().order_by("-created_at")

    def get_queryset(self):
        user = self.request.user
        queryset = super().get_queryset()
        if getattr(user, "role", None) == "customer":
            return queryset.filter(customer_id=user.id)
        return queryset

    def perform_create(self, serializer):
        user = self.request.user
        customer_id = serializer.validated_data.get("customer_id")
        if getattr(user, "role", None) == "customer":
            customer_id = user.id
        serializer.save(customer_id=customer_id)

    @action(detail=True, methods=["post"])
    def approve(self, request, pk=None):
        return self._set_status(ProductReview.Status.APPROVED)

    @action(detail=True, methods=["post"])
    def reject(self, request, pk=None):
        return self._set_status(ProductReview.Status.REJECTED)

    def _set_status(self, target_status):
        review = self.get_object()
        review.status = target_status
        review.save(update_fields=["status", "updated_at"])
        return Response(self.get_serializer(review).data, status=status.HTTP_200_OK)
