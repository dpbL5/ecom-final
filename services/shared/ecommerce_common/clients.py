import requests
from django.conf import settings


class ServiceClientError(RuntimeError):
    pass


class ServiceClient:
    # Wrapper nho quanh requests de cac service goi nhau bang REST co cung timeout/header.
    def __init__(self, base_url, timeout=None):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout or settings.SERVICE_HTTP_TIMEOUT

    def request(self, method, path, *, token=None, json=None, params=None):
        headers = {"Accept": "application/json"}
        if token:
            # Forward JWT cua user sang service tiep theo de service do van biet ai dang thao tac.
            headers["Authorization"] = f"Bearer {token}"

        response = requests.request(
            method=method,
            url=f"{self.base_url}{path}",
            json=json,
            params=params,
            headers=headers,
            timeout=self.timeout,
        )
        if response.status_code >= 400:
            raise ServiceClientError(
                f"{method} {path} failed with {response.status_code}: {response.text}"
            )
        if response.status_code == 204:
            return None
        return response.json()


def bearer_token_from_request(request):
    # Lay phan token thuan tu header "Bearer <token>" de forward qua ServiceClient.
    header = request.headers.get("Authorization", "")
    if header.startswith("Bearer "):
        return header.removeprefix("Bearer ").strip()
    return None
