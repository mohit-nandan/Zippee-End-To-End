import requests


class BaseClient:
    def __init__(self, base_url: str, token: str = None):
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()
        if token:
            self.session.headers.update({"Authorization": f"Bearer {token}"})
        self.session.headers.update({"Content-Type": "application/json"})

    def get(self, path: str, expected_status: int = 200, **kwargs) -> dict:
        response = self.session.get(f"{self.base_url}{path}", **kwargs)
        self._assert_status(response, expected_status)
        return response.json()

    def post(self, path: str, expected_status: int = 201, **kwargs) -> dict:
        response = self.session.post(f"{self.base_url}{path}", **kwargs)
        self._assert_status(response, expected_status)
        return response.json()

    def put(self, path: str, expected_status: int = 200, **kwargs) -> dict:
        response = self.session.put(f"{self.base_url}{path}", **kwargs)
        self._assert_status(response, expected_status)
        return response.json()

    def patch(self, path: str, expected_status: int = 200, **kwargs) -> dict:
        response = self.session.patch(f"{self.base_url}{path}", **kwargs)
        self._assert_status(response, expected_status)
        return response.json()

    def _assert_status(self, response: requests.Response, expected: int):
        assert response.status_code == expected, (
            f"Expected {expected}, got {response.status_code}. "
            f"URL: {response.url}. Body: {response.text[:500]}"
        )
