from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from ecommerce_common.test_utils import authenticated_client

from .models import Category


class CatalogStaffAdminPermissionTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Books", slug="books")

    def product_payload(self, sku):
        slug = sku.lower()
        return {
            "category": str(self.category.id),
            "sku": sku,
            "name": f"Product {sku}",
            "slug": slug,
            "description": "Created by role test",
            "brand": "Demo",
            "product_type": "book",
            "status": "published",
            "attributes": {},
            "image_urls": [],
        }

    def test_public_users_can_read_catalog(self):
        response = APIClient().get("/api/v1/products/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_customer_cannot_create_product(self):
        client, _ = authenticated_client("customer")

        response = client.post("/api/v1/products/", self.product_payload("CUS-001"), format="json")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_staff_and_admin_can_create_product(self):
        for role in ("staff", "admin"):
            with self.subTest(role=role):
                client, principal = authenticated_client(role)
                response = client.post("/api/v1/products/", self.product_payload(f"{role.upper()}-001"), format="json")

                self.assertEqual(response.status_code, status.HTTP_201_CREATED)
                self.assertEqual(response.data["created_by"], principal["id"])
