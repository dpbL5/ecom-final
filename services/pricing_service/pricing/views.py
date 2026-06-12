from decimal import Decimal

from django.db import models
from django.utils import timezone
from rest_framework import status, views, viewsets
from rest_framework.response import Response

from .models import Coupon, PriceBook, ProductPrice, PromotionCampaign
from .serializers import (
    CouponSerializer,
    PriceBookSerializer,
    ProductPriceSerializer,
    PromotionCampaignSerializer,
    QuoteRequestSerializer,
    calculate_discount,
)


class PriceBookViewSet(viewsets.ModelViewSet):
    queryset = PriceBook.objects.all().order_by("code")
    serializer_class = PriceBookSerializer


class ProductPriceViewSet(viewsets.ModelViewSet):
    queryset = ProductPrice.objects.select_related("price_book").all().order_by("sku")
    serializer_class = ProductPriceSerializer


class PromotionCampaignViewSet(viewsets.ModelViewSet):
    queryset = PromotionCampaign.objects.all().order_by("-created_at")
    serializer_class = PromotionCampaignSerializer


class CouponViewSet(viewsets.ModelViewSet):
    queryset = Coupon.objects.select_related("campaign").all().order_by("-created_at")
    serializer_class = CouponSerializer


class QuoteView(views.APIView):
    def post(self, request):
        serializer = QuoteRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        now = timezone.now()
        coupon = None
        if data.get("coupon_code"):
            coupon = Coupon.objects.select_related("campaign").filter(
                code=data["coupon_code"],
                is_active=True,
                campaign__is_active=True,
                redeemed_count__lt=models.F("max_redemptions"),
            ).first()

        quoted_items = []
        subtotal = Decimal("0.00")
        for item in data["items"]:
            price = ProductPrice.objects.select_related("price_book").filter(
                sku=item["sku"],
                is_active=True,
                price_book__is_active=True,
            ).filter(
                models.Q(starts_at__isnull=True) | models.Q(starts_at__lte=now),
                models.Q(ends_at__isnull=True) | models.Q(ends_at__gte=now),
            ).order_by("-created_at").first()
            if not price:
                return Response({"detail": f"No active price for SKU {item['sku']}."}, status=status.HTTP_404_NOT_FOUND)
            line_total = price.amount * item["quantity"]
            subtotal += line_total
            quoted_items.append({
                "sku": item["sku"],
                "quantity": item["quantity"],
                "unit_price": str(price.amount),
                "line_total": str(line_total),
                "currency": price.price_book.currency,
            })

        discount_total = calculate_discount(subtotal, coupon)
        total = subtotal - discount_total
        currency = quoted_items[0]["currency"] if quoted_items else "VND"
        return Response({
            "currency": currency,
            "subtotal": str(subtotal),
            "discount_total": str(discount_total),
            "total": str(total),
            "items": quoted_items,
        })
