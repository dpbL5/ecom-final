from rest_framework import permissions, viewsets

from ecommerce_common.permissions import IsAdminOrStaff

from .models import Category, Product, ProductVariant
from .serializers import CategorySerializer, ProductSerializer, ProductVariantSerializer


class CatalogWritePermissionMixin:
    def get_permissions(self):
        # Khach vang lai duoc xem catalog, nhung tao/sua/xoa san pham chi danh cho admin/staff.
        if self.action in {"list", "retrieve"}:
            return [permissions.AllowAny()]
        return [IsAdminOrStaff()]


class CategoryViewSet(CatalogWritePermissionMixin, viewsets.ModelViewSet):
    queryset = Category.objects.all().order_by("name")
    serializer_class = CategorySerializer


class ProductViewSet(CatalogWritePermissionMixin, viewsets.ModelViewSet):
    queryset = Product.objects.select_related("category").prefetch_related("variants").all().order_by("-created_at")
    serializer_class = ProductSerializer

    def perform_create(self, serializer):
        serializer.save(created_by=getattr(self.request.user, "id", None))


class ProductVariantViewSet(CatalogWritePermissionMixin, viewsets.ModelViewSet):
    queryset = ProductVariant.objects.select_related("product").all().order_by("-created_at")
    serializer_class = ProductVariantSerializer
