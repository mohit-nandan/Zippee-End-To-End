"""
Shared fixtures for direct API tests (tests/api/internal/ and tests/api/integrations/).
Auth and base URL come from the global cfg fixture in fixtures/api_fixtures.py.
"""
import pytest
import requests


@pytest.fixture(scope="session")
def api_base_url(cfg):
    return cfg["internal_api_url"].rstrip("/")


@pytest.fixture(scope="session")
def auth_headers(cfg):
    token = cfg.get("x_api_key") or cfg.get("admin_pass")
    return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}


@pytest.fixture(scope="session")
def api_session(api_base_url, auth_headers):
    session = requests.Session()
    session.headers.update(auth_headers)
    yield session
    session.close()
