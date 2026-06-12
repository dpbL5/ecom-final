from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from ecommerce_common.test_utils import authenticated_client

from .models import BackofficeWorkItem


class BackofficeStaffAdminPermissionTests(TestCase):
    def setUp(self):
        BackofficeWorkItem.objects.create(
            context="order",
            aggregate_type="Order",
            title="Check pending order",
            description="Operational test item",
        )

    def test_work_items_are_visible_only_to_staff_and_admin(self):
        self.assertEqual(APIClient().get("/api/v1/work-items/").status_code, status.HTTP_403_FORBIDDEN)

        customer_client, _ = authenticated_client("customer")
        self.assertEqual(customer_client.get("/api/v1/work-items/").status_code, status.HTTP_403_FORBIDDEN)

        for role in ("staff", "admin"):
            with self.subTest(role=role):
                client, _ = authenticated_client(role)
                response = client.get("/api/v1/work-items/")

                self.assertEqual(response.status_code, status.HTTP_200_OK)
                self.assertEqual(response.data["count"], 1)

    def test_audit_log_actor_is_taken_from_staff_or_admin_token(self):
        client, principal = authenticated_client("admin")

        response = client.post(
            "/api/v1/audit-logs/",
            {
                "action": "catalog.product.created",
                "context": "catalog",
                "aggregate_type": "Product",
                "before": {},
                "after": {"sku": "ADMIN-001"},
                "metadata": {},
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["actor_id"], principal["id"])
        self.assertEqual(response.data["actor_role"], "admin")
