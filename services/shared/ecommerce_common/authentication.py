from dataclasses import dataclass

import jwt
from django.conf import settings
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed


@dataclass(frozen=True)
class Principal:
    # Object nhe thay the User model o cac service khong co bang users.
    # DRF gan object nay vao request.user sau khi JWT hop le.
    id: str
    email: str
    role: str
    claims: dict

    @property
    def is_authenticated(self):
        return True


class ServiceJWTAuthentication(BaseAuthentication):
    keyword = "Bearer"

    def authenticate(self, request):
        # Neu khong co Authorization header, DRF se tiep tuc xu ly nhu request chua dang nhap.
        header = request.headers.get("Authorization", "")
        if not header:
            return None

        parts = header.split()
        if len(parts) != 2 or parts[0] != self.keyword:
            raise AuthenticationFailed("Invalid Authorization header.")

        try:
            # Decode token bang shared signing key. Cac service khong can goi identity-service de kiem tra token.
            claims = jwt.decode(
                parts[1],
                settings.JWT_SIGNING_KEY,
                algorithms=[settings.JWT_ALGORITHM],
                options={"verify_aud": False},
            )
        except jwt.ExpiredSignatureError as exc:
            raise AuthenticationFailed("Token has expired.") from exc
        except jwt.InvalidTokenError as exc:
            raise AuthenticationFailed("Invalid token.") from exc

        # SimpleJWT luu user id trong claim user_id; sub duoc ho tro them de linh hoat.
        user_id = str(claims.get("user_id") or claims.get("sub") or "")
        email = claims.get("email") or ""
        role = claims.get("role") or "customer"
        if not user_id:
            raise AuthenticationFailed("Token is missing user identity.")

        return Principal(id=user_id, email=email, role=role, claims=claims), claims
