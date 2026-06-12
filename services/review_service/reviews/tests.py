import uuid

from django.test import TestCase
from rest_framework import status

from ecommerce_common.test_utils import authenticated_client

from .models import ProductReview


class ReviewStaffAdminPermissionTests(TestCase):
    def setUp(self):
        self.customer_id = uuid.uuid4()
        self.other_customer_id = uuid.uuid4()
        product_id = uuid.uuid4()
        self.own_review = ProductReview.objects.create(
            product_id=product_id,
            customer_id=self.customer_id,
            order_id=uuid.uuid4(),
            rating=5,
            title="Good",
        )
        self.other_review = ProductReview.objects.create(
            product_id=product_id,
            customer_id=self.other_customer_id,
            order_id=uuid.uuid4(),
            rating=4,
            title="Also good",
        )

    def test_customer_sees_only_own_reviews_but_staff_and_admin_see_all(self):
        customer_client, _ = authenticated_client("customer", user_id=self.customer_id)
        response = customer_client.get("/api/v1/reviews/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["id"], str(self.own_review.id))

        for role in ("staff", "admin"):
            with self.subTest(role=role):
                client, _ = authenticated_client(role)
                response = client.get("/api/v1/reviews/")

                self.assertEqual(response.status_code, status.HTTP_200_OK)
                self.assertEqual(response.data["count"], 2)

    def test_customer_cannot_approve_review_but_staff_can(self):
        customer_client, _ = authenticated_client("customer", user_id=self.customer_id)
        response = customer_client.post(f"/api/v1/reviews/{self.own_review.id}/approve/", {}, format="json")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        staff_client, _ = authenticated_client("staff")
        response = staff_client.post(f"/api/v1/reviews/{self.own_review.id}/approve/", {}, format="json")
        self.own_review.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.own_review.status, ProductReview.Status.APPROVED)
