from django.test import TestCase
from rest_framework import status

from ecommerce_common.test_utils import authenticated_client

from .models import PriceBook


class PricingStaffAdminPermissionTests(TestCase):
    def setUp(self):
        PriceBook.objects.create(code="BASE", name="Base VND", currency="VND")

    def test_customer_can_read_but_cannot_create_price_book(self):
        customer_client, _ = authenticated_client("customer")

        self.assertEqual(customer_client.get("/api/v1/price-books/").status_code, status.HTTP_200_OK)

        response = customer_client.post(
            "/api/v1/price-books/",
            {"code": "CUSTOMER", "name": "Customer book", "currency": "VND"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_staff_and_admin_can_create_price_book(self):
        for role in ("staff", "admin"):
            with self.subTest(role=role):
                client, _ = authenticated_client(role)
                response = client.post(
                    "/api/v1/price-books/",
                    {"code": role.upper(), "name": f"{role} book", "currency": "VND"},
                    format="json",
                )

                self.assertEqual(response.status_code, status.HTTP_201_CREATED)
