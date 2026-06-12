import uuid

from django.test import TestCase
from rest_framework import status

from ecommerce_common.test_utils import authenticated_client

from .models import ReturnRequest


class ReturnStaffAdminPermissionTests(TestCase):
    def setUp(self):
        self.customer_id = uuid.uuid4()
        self.return_request = ReturnRequest.objects.create(
            order_id=uuid.uuid4(),
            customer_id=self.customer_id,
            reason="Wrong size",
            idempotency_key="return-001",
        )

    def test_customer_cannot_approve_return_but_staff_can(self):
        customer_client, _ = authenticated_client("customer", user_id=self.customer_id)
        response = customer_client.post(f"/api/v1/returns/{self.return_request.id}/approve/", {}, format="json")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        staff_client, _ = authenticated_client("staff")
        response = staff_client.post(f"/api/v1/returns/{self.return_request.id}/approve/", {}, format="json")
        self.return_request.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.return_request.status, ReturnRequest.Status.APPROVED)
