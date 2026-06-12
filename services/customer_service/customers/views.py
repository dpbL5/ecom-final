from rest_framework import viewsets

from .models import Address, CustomerProfile, WishlistItem
from .serializers import AddressSerializer, CustomerProfileSerializer, WishlistItemSerializer


class CustomerOwnedQuerysetMixin:
    customer_field = "customer__user_id"

    def filter_customer_scope(self, queryset):
        user = self.request.user
        if getattr(user, "role", None) == "customer":
            return queryset.filter(**{self.customer_field: user.id})
        return queryset


class CustomerProfileViewSet(viewsets.ModelViewSet):
    serializer_class = CustomerProfileSerializer
    queryset = CustomerProfile.objects.all().order_by("-created_at")

    def get_queryset(self):
        user = self.request.user
        queryset = super().get_queryset()
        if getattr(user, "role", None) == "customer":
            return queryset.filter(user_id=user.id)
        return queryset

    def perform_create(self, serializer):
        user = self.request.user
        if getattr(user, "role", None) == "customer":
            serializer.save(user_id=user.id, email=user.email)
        else:
            serializer.save()


class AddressViewSet(CustomerOwnedQuerysetMixin, viewsets.ModelViewSet):
    serializer_class = AddressSerializer
    queryset = Address.objects.select_related("customer").all().order_by("-created_at")

    def get_queryset(self):
        return self.filter_customer_scope(super().get_queryset())


class WishlistItemViewSet(CustomerOwnedQuerysetMixin, viewsets.ModelViewSet):
    serializer_class = WishlistItemSerializer
    queryset = WishlistItem.objects.select_related("customer").all().order_by("-created_at")

    def get_queryset(self):
        return self.filter_customer_scope(super().get_queryset())
