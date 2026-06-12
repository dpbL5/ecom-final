from django.test import TestCase
from rest_framework import status

from ecommerce_common.test_utils import authenticated_client

from .models import Warehouse


class InventoryStaffAdminPermissionTests(TestCase):
    def setUp(self):
        Warehouse.objects.create(code="HCM", name="Ho Chi Minh")

    def test_customer_can_read_but_cannot_create_warehouse(self):
        customer_client, _ = authenticated_client("customer")

        self.assertEqual(customer_client.get("/api/v1/warehouses/").status_code, status.HTTP_200_OK)

        response = customer_client.post(
            "/api/v1/warehouses/",
            {"code": "HN", "name": "Ha Noi", "city": "Ha Noi", "country": "VN"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_staff_and_admin_can_create_warehouse(self):
        for role in ("staff", "admin"):
            with self.subTest(role=role):
                client, _ = authenticated_client(role)
                response = client.post(
                    "/api/v1/warehouses/",
                    {"code": f"{role.upper()}-WH", "name": f"{role} warehouse", "country": "VN"},
                    format="json",
                )

                self.assertEqual(response.status_code, status.HTTP_201_CREATED)
