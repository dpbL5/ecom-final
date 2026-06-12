from django.db.models import Q
from rest_framework import permissions, views, viewsets
from rest_framework.response import Response

from ecommerce_common.permissions import IsAdminOrStaff

from .models import SearchProductDocument
from .serializers import SearchProductDocumentSerializer


class ProductDocumentViewSet(viewsets.ModelViewSet):
    queryset = SearchProductDocument.objects.all().order_by("-updated_at")
    serializer_class = SearchProductDocumentSerializer

    def get_permissions(self):
        if self.action in {"list", "retrieve"}:
            return [permissions.AllowAny()]
        return [IsAdminOrStaff()]


class SearchView(views.APIView):
    # Public endpoint: nguoi dung chua dang nhap van co the tim san pham.
    authentication_classes = []
    permission_classes = []

    def get(self, request):
        # Search service doc tu search document snapshot, khong query truc tiep catalog/pricing/inventory.
        queryset = SearchProductDocument.objects.filter(status="published")
        query = request.query_params.get("q")
        if query:
            queryset = queryset.filter(
                Q(name__icontains=query)
                | Q(sku__icontains=query)
                | Q(description__icontains=query)
                | Q(brand__icontains=query)
                | Q(search_text__icontains=query)
            )
        sku = request.query_params.get("sku")
        if sku:
            skus = [item.strip() for item in sku.split(",") if item.strip()]
            if skus:
                queryset = queryset.filter(sku__in=skus)
        product_type = request.query_params.get("type")
        if product_type:
            queryset = queryset.filter(product_type=product_type)
        brand = request.query_params.get("brand")
        if brand:
            queryset = queryset.filter(brand=brand)
        serializer = SearchProductDocumentSerializer(queryset.order_by("name")[:100], many=True)
        return Response(serializer.data)
