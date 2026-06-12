from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from ecommerce_common.test_utils import authenticated_client

from .models import Carrier


class ShippingStaffAdminPermissionTests(TestCase):
    def setUp(self):
        Carrier.objects.create(code="GHN", name="Giao Hang Nhanh")

    def test_carriers_are_visible_only_to_staff_and_admin(self):
        self.assertEqual(APIClient().get("/api/v1/carriers/").status_code, status.HTTP_403_FORBIDDEN)

        customer_client, _ = authenticated_client("customer")
        self.assertEqual(customer_client.get("/api/v1/carriers/").status_code, status.HTTP_403_FORBIDDEN)

        for role in ("staff", "admin"):
            with self.subTest(role=role):
                client, _ = authenticated_client(role)
                response = client.get("/api/v1/carriers/")

                self.assertEqual(response.status_code, status.HTTP_200_OK)
                self.assertEqual(response.data["count"], 1)
