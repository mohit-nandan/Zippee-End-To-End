"""
Network interception utility for web UI tests.
Captures API requests/responses during Playwright test execution
and provides structured assertions on status codes and response bodies.
"""
import json
from dataclasses import dataclass, field
from typing import Optional
from playwright.sync_api import Page, Request, Response


@dataclass
class CapturedCall:
    url: str
    method: str
    status: int
    request_body: Optional[dict] = None
    response_body: Optional[dict] = None
    headers: dict = field(default_factory=dict)

    @property
    def is_success(self) -> bool:
        return 200 <= self.status < 300

    @property
    def is_client_error(self) -> bool:
        return 400 <= self.status < 500

    @property
    def is_server_error(self) -> bool:
        return self.status >= 500


class ApiInterceptor:
    """
    Attaches to a Playwright page and records all matching API calls.

    Usage:
        interceptor = ApiInterceptor(page)
        interceptor.watch("/api/")
        page.goto(url)
        interceptor.assert_no_errors()
        call = interceptor.get("/brand")
        assert call.status == 200
        assert "data" in call.response_body
    """

    def __init__(self, page: Page):
        self._page = page
        self._calls: list[CapturedCall] = []
        self._patterns: list[str] = []
        self._attached = False

    def watch(self, *url_patterns: str) -> "ApiInterceptor":
        self._patterns = list(url_patterns) if url_patterns else [""]
        if not self._attached:
            self._page.on("response", self._on_response)
            self._attached = True
        return self

    def _matches(self, url: str) -> bool:
        if not self._patterns:
            return True
        return any(p in url for p in self._patterns)

    def _on_response(self, response: Response):
        if not self._matches(response.url):
            return
        try:
            req_body = None
            try:
                raw = response.request.post_data
                if raw:
                    req_body = json.loads(raw)
            except Exception:
                pass

            resp_body = None
            try:
                ct = response.headers.get("content-type", "")
                if "json" in ct:
                    resp_body = response.json()
            except Exception:
                pass

            self._calls.append(CapturedCall(
                url=response.url,
                method=response.request.method,
                status=response.status,
                request_body=req_body,
                response_body=resp_body,
                headers=dict(response.headers),
            ))
        except Exception:
            pass

    # ── Query helpers ──────────────────────────────────────────────────────

    def all(self) -> list[CapturedCall]:
        return list(self._calls)

    def get(self, path: str) -> Optional[CapturedCall]:
        """Return the last call whose URL contains `path`."""
        matches = [c for c in self._calls if path in c.url]
        return matches[-1] if matches else None

    def get_all(self, path: str) -> list[CapturedCall]:
        return [c for c in self._calls if path in c.url]

    def errors(self) -> list[CapturedCall]:
        return [c for c in self._calls if c.status >= 400]

    def server_errors(self) -> list[CapturedCall]:
        return [c for c in self._calls if c.is_server_error]

    def clear(self):
        self._calls.clear()

    # ── Assertion helpers ─────────────────────────────────────────────────

    def assert_no_errors(self, exclude: list[str] = None):
        exclude = exclude or []
        bad = [
            c for c in self.errors()
            if not any(ex in c.url for ex in exclude)
        ]
        assert bad == [], (
            "Unexpected API errors:\n" +
            "\n".join(f"  {c.method} {c.url} → {c.status}" for c in bad)
        )

    def assert_no_server_errors(self):
        bad = self.server_errors()
        assert bad == [], (
            "Server errors (5xx):\n" +
            "\n".join(f"  {c.method} {c.url} → {c.status}" for c in bad)
        )

    def assert_called(self, path: str, method: str = None):
        calls = self.get_all(path)
        if method:
            calls = [c for c in calls if c.method.upper() == method.upper()]
        assert calls, f"Expected API call to '{path}' (method={method}) but none found"

    def assert_status(self, path: str, expected_status: int):
        call = self.get(path)
        assert call is not None, f"No API call to '{path}' was captured"
        assert call.status == expected_status, (
            f"Expected {path} → {expected_status}, got {call.status}"
        )

    def assert_response_key(self, path: str, key: str):
        call = self.get(path)
        assert call is not None, f"No call to '{path}' captured"
        assert call.response_body is not None, f"Response body for '{path}' is not JSON"
        assert key in call.response_body, (
            f"Key '{key}' missing from {path} response. Got keys: {list(call.response_body.keys())}"
        )

    def assert_response_value(self, path: str, key: str, expected):
        call = self.get(path)
        assert call is not None
        assert call.response_body is not None
        actual = call.response_body.get(key)
        assert actual == expected, (
            f"{path} → response['{key}'] expected {expected!r}, got {actual!r}"
        )
