from decimal import Decimal
import uuid

from django.test import TestCase
from rest_framework import status

from ecommerce_common.test_utils import authenticated_client

from .models import Order


class OrderStaffAdminPermissionTests(TestCase):
    def setUp(self):
        self.customer_id = uuid.uuid4()
        self.other_customer_id = uuid.uuid4()
        self.own_order = self.create_order("own", self.customer_id, Order.Status.PAID)
        self.other_order = self.create_order("other", self.other_customer_id, Order.Status.PAID)

    def create_order(self, suffix, customer_id, order_status):
        return Order.objects.create(
            customer_id=customer_id,
            status=order_status,
            currency="VND",
            subtotal=Decimal("100000.00"),
            discount_total=Decimal("0.00"),
            shipping_fee=Decimal("0.00"),
            grand_total=Decimal("100000.00"),
            shipping_address={"line1": "Test"},
            idempotency_key=f"order-{suffix}",
            metadata={},
        )

    def test_customer_sees_only_own_orders_but_staff_and_admin_see_all(self):
        customer_client, _ = authenticated_client("customer", user_id=self.customer_id)
        response = customer_client.get("/api/v1/orders/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["id"], str(self.own_order.id))

        for role in ("staff", "admin"):
            with self.subTest(role=role):
                client, _ = authenticated_client(role)
                response = client.get("/api/v1/orders/")

                self.assertEqual(response.status_code, status.HTTP_200_OK)
                self.assertEqual(response.data["count"], 2)

    def test_customer_cannot_confirm_order_but_staff_can(self):
        customer_client, _ = authenticated_client("customer", user_id=self.customer_id)
        response = customer_client.post(f"/api/v1/orders/{self.own_order.id}/confirm/", {"note": "try"}, format="json")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        staff_client, staff = authenticated_client("staff")
        response = staff_client.post(f"/api/v1/orders/{self.own_order.id}/confirm/", {"note": "ok"}, format="json")
        self.own_order.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.own_order.status, Order.Status.CONFIRMED)
        history = self.own_order.status_history.latest("created_at")
        self.assertEqual(str(history.actor_id), staff["id"])
