from django.conf import settings
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from ecommerce_common.clients import ServiceClient, ServiceClientError, bearer_token_from_request

from .models import Cart, CartItem
from .serializers import CartItemSerializer, CartSerializer, CheckoutSerializer


class CartViewSet(viewsets.ModelViewSet):
    serializer_class = CartSerializer
    queryset = Cart.objects.prefetch_related("items").all().order_by("-created_at")

    def get_queryset(self):
        user = self.request.user
        queryset = super().get_queryset()
        # Customer chi thay gio hang cua minh; staff/admin co the xem tat ca de ho tro van hanh.
        if getattr(user, "role", None) == "customer":
            return queryset.filter(customer_id=user.id)
        return queryset

    def perform_create(self, serializer):
        user = self.request.user
        if getattr(user, "role", None) == "customer":
            serializer.save(customer_id=user.id)
        else:
            serializer.save()

    @action(detail=True, methods=["post"])
    def checkout(self, request, pk=None):
        # Checkout la orchestration: cart-service dieu phoi pricing, order va inventory qua REST.
        cart = self.get_object()
        if cart.status != Cart.Status.ACTIVE:
            return Response({"detail": "Cart is not active."}, status=status.HTTP_409_CONFLICT)
        if not cart.items.exists():
            return Response({"detail": "Cart is empty."}, status=status.HTTP_409_CONFLICT)

        serializer = CheckoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        token = bearer_token_from_request(request)
        items = list(cart.items.all())
        quote_items = [{"sku": item.sku, "quantity": item.quantity} for item in items]

        # Lay URL cac service tu settings.SERVICE_URLS de code khong phu thuoc truc tiep vao host/port local.
        pricing_client = ServiceClient(settings.SERVICE_URLS["pricing"])
        order_client = ServiceClient(settings.SERVICE_URLS["order"])
        inventory_client = ServiceClient(settings.SERVICE_URLS["inventory"])

        try:
            # 1) Lay gia moi nhat va discount tu pricing-service truoc khi tao order.
            quote = pricing_client.request(
                "POST",
                "/api/v1/quote/",
                token=token,
                json={"items": quote_items, "coupon_code": data.get("coupon_code", "")},
            )
            quoted_by_sku = {item["sku"]: item for item in quote["items"]}
            # 2) Tao order snapshot: order luu lai gia, ten san pham va dia chi tai thoi diem checkout.
            order = order_client.request(
                "POST",
                "/api/v1/orders/",
                token=token,
                json={
                    "customer_id": str(cart.customer_id or request.user.id),
                    "currency": quote["currency"],
                    "subtotal": quote["subtotal"],
                    "discount_total": quote["discount_total"],
                    "shipping_fee": "0.00",
                    "grand_total": quote["total"],
                    "shipping_address": data["shipping_address"],
                    "idempotency_key": data["idempotency_key"],
                    "metadata": {"cart_id": str(cart.id)},
                    "lines": [
                        {
                            "product_id": str(item.product_id),
                            "sku": item.sku,
                            "product_name": item.product_name,
                            "quantity": item.quantity,
                            "unit_price": quoted_by_sku[item.sku]["unit_price"],
                            "line_total": quoted_by_sku[item.sku]["line_total"],
                            "attributes_snapshot": item.attributes_snapshot,
                        }
                        for item in items
                    ],
                },
            )
            for item in items:
                # 3) Giu hang cho tung SKU. Idempotency key giup retry khong tao trung reservation.
                inventory_client.request(
                    "POST",
                    "/api/v1/stock/reserve/",
                    token=token,
                    json={
                        "sku": item.sku,
                        "order_id": order["id"],
                        "quantity": item.quantity,
                        "idempotency_key": f"{order['id']}:{item.sku}",
                    },
                )
        except ServiceClientError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_502_BAD_GATEWAY)

        cart.status = Cart.Status.CHECKED_OUT
        cart.save(update_fields=["status", "updated_at"])
        # Tra ve ca order va quote de frontend co du thong tin hien thi buoc tiep theo.
        return Response({"order": order, "quote": quote})


class CartItemViewSet(viewsets.ModelViewSet):
    serializer_class = CartItemSerializer
    queryset = CartItem.objects.select_related("cart").all().order_by("-created_at")

    def get_queryset(self):
        user = self.request.user
        queryset = super().get_queryset()
        if getattr(user, "role", None) == "customer":
            return queryset.filter(cart__customer_id=user.id)
        return queryset
