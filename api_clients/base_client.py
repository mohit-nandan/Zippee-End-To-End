import requests


class BaseClient:
    def __init__(self, base_url: str, token: str = None):
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()
        if token:
            self.session.headers.update({"Authorization": f"Bearer {token}"})

    def get(self, path: str, expected_status: int = 200, **kwargs) -> dict | None:
        response = self.session.get(f"{self.base_url}{path}", **kwargs)
        self._assert_status(response, expected_status)
        return self._parse_response(response)

    def post(self, path: str, expected_status: int = 201, **kwargs) -> dict | None:
        kwargs.setdefault("headers", {})["Content-Type"] = "application/json"
        response = self.session.post(f"{self.base_url}{path}", **kwargs)
        self._assert_status(response, expected_status)
        return self._parse_response(response)

    def put(self, path: str, expected_status: int = 200, **kwargs) -> dict | None:
        kwargs.setdefault("headers", {})["Content-Type"] = "application/json"
        response = self.session.put(f"{self.base_url}{path}", **kwargs)
        self._assert_status(response, expected_status)
        return self._parse_response(response)

    def patch(self, path: str, expected_status: int = 200, **kwargs) -> dict | None:
        kwargs.setdefault("headers", {})["Content-Type"] = "application/json"
        response = self.session.patch(f"{self.base_url}{path}", **kwargs)
        self._assert_status(response, expected_status)
        return self._parse_response(response)

    def delete(self, path: str, expected_status: int = 204, **kwargs) -> dict | None:
        response = self.session.delete(f"{self.base_url}{path}", **kwargs)
        self._assert_status(response, expected_status)
        return self._parse_response(response)

    def _assert_status(self, response: requests.Response, expected: int):
        assert response.status_code == expected, (
            f"Expected {expected}, got {response.status_code} "
            f"[{response.request.method}] {response.url} — Body: {response.text[:500]}"
        )

    def _parse_response(self, response: requests.Response) -> dict | None:
        if not response.content:
            return None
        try:
            return response.json()
        except ValueError as exc:
            raise ValueError(
                f"Non-JSON response from [{response.request.method}] {response.url} "
                f"(status {response.status_code}): {response.text[:200]}"
            ) from exc

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.session.close()
