"""
Fixtures for network interception tests.
Provides an authenticated browser page + a pre-wired ApiInterceptor.
"""
import pytest
from utils.web_api_interceptor import ApiInterceptor
from utils.helpers import get_screen_size


@pytest.fixture(scope="session")
def network_screen_size() -> dict:
    w, h = get_screen_size()
    return {"width": w, "height": h}


@pytest.fixture
def network_page(browser_instance, web_cfg, network_screen_size):
    """
    Authenticated Playwright page for network tests.
    Logs in once per test, yields the ready page.
    """
    context = browser_instance.new_context(viewport=network_screen_size)
    pg = context.new_page()
    base = web_cfg["dashboard_url"].rstrip("/")

    pg.goto(f"{base}/sign-in")
    pg.wait_for_load_state("domcontentloaded")
    pg.locator("#email").wait_for(state="visible", timeout=15000)
    pg.locator("#email").fill(web_cfg["admin_user"])
    pg.get_by_role("button", name="Continue with Email").click()
    pg.locator("input[type='password']").wait_for(state="visible", timeout=8000)
    pg.locator("input[type='password']").fill(web_cfg["admin_pass"])
    pg.get_by_role("button", name="Login", exact=True).click()
    pg.wait_for_url(f"{base}/", timeout=15000)

    yield pg
    context.close()


@pytest.fixture
def interceptor(network_page):
    """ApiInterceptor pre-attached to the authenticated network_page."""
    return ApiInterceptor(network_page)
