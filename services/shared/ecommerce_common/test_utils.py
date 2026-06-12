import uuid

import jwt
from django.conf import settings
from rest_framework.test import APIClient


def make_principal(role, *, user_id=None, email=None):
    user_id = str(user_id or uuid.uuid4())
    return {
        "id": user_id,
        "email": email or f"{role}@example.com",
        "role": role,
    }


def make_token(role, *, user_id=None, email=None):
    principal = make_principal(role, user_id=user_id, email=email)
    token = jwt.encode(
        {
            "user_id": principal["id"],
            "email": principal["email"],
            "role": principal["role"],
        },
        settings.JWT_SIGNING_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )
    return token, principal


def authenticated_client(role, *, user_id=None, email=None):
    token, principal = make_token(role, user_id=user_id, email=email)
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
    return client, principal
