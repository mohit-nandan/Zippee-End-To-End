"""
Web test fixtures — scoped correctly so login happens ONCE per session,
not once per test (which would be 130× slower).

Fixture scoping strategy:
  - browser_instance  → session  (one browser process)
  - web_cfg           → session  (config loaded once)
  - auth_storage      → session  (login once, save storage state)
  - authenticated_page→ function (fresh page per test, with saved auth cookies)
  - authenticated_dashboard → alias for authenticated_page (backward compat)
  - page              → function (unauthenticated, for login/negative tests)
"""
import os
import pytest
import allure
from playwright.sync_api import sync_playwright, BrowserContext
from utils.config_loader import get_config
from utils.helpers import get_screen_size


# ── Session-level fixtures ────────────────────────────────────────────────────

@pytest.fixture(scope="session")
def screen_size() -> dict:
    w, h = get_screen_size()
    return {"width": w, "height": h}


@pytest.fixture(scope="session")
def web_cfg():
    env = os.getenv("ENV", "preprod")
    return get_config(env)


@pytest.fixture(scope="session")
def playwright_instance():
    with sync_playwright() as pw:
        yield pw


@pytest.fixture(scope="session")
def browser_instance(playwright_instance, screen_size):
    browser = playwright_instance.chromium.launch(
        headless=False,
        args=[
            "--no-sandbox",
            "--disable-dev-shm-usage",
            f"--window-size={screen_size['width']},{screen_size['height']}",
        ],
    )
    yield browser
    browser.close()


@pytest.fixture(scope="session")
def auth_storage_path(tmp_path_factory):
    return str(tmp_path_factory.mktemp("auth") / "storage_state.json")


@pytest.fixture(scope="session")
def authenticated_session(browser_instance, web_cfg, auth_storage_path, screen_size):
    """
    Logs in ONCE for the entire test session and saves browser storage state.
    All subsequent tests restore from this state — no repeated logins.
    """
    context: BrowserContext = browser_instance.new_context(viewport=screen_size)
    page = context.new_page()
    base = web_cfg["dashboard_url"].rstrip("/")

    with allure.step("Session login"):
        page.goto(f"{base}/sign-in")
        page.wait_for_load_state("domcontentloaded")
        page.locator("#email").wait_for(state="visible", timeout=15000)
        page.locator("#email").fill(web_cfg["admin_user"])
        page.get_by_role("button", name="Continue with Email").click()
        page.locator("input[type='password']").wait_for(state="visible", timeout=8000)
        page.locator("input[type='password']").fill(web_cfg["admin_pass"])
        page.get_by_role("button", name="Login", exact=True).click()
        page.wait_for_url(f"{base}/", timeout=15000)

    context.storage_state(path=auth_storage_path)
    context.close()
    return auth_storage_path


# ── Function-level fixtures ───────────────────────────────────────────────────

@pytest.fixture
def page(browser_instance, screen_size):
    """Unauthenticated page — used for login tests and negative scenarios."""
    context = browser_instance.new_context(viewport=screen_size)
    pg = context.new_page()
    yield pg
    context.close()


@pytest.fixture
def authenticated_dashboard(browser_instance, authenticated_session, screen_size):
    """
    Authenticated page — restores session state so no login needed.
    Fresh page context per test to ensure test isolation.
    """
    context = browser_instance.new_context(
        viewport=screen_size,
        storage_state=authenticated_session,
    )
    pg = context.new_page()
    yield pg
    context.close()


# ── Allure screenshot on failure ──────────────────────────────────────────────

@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    if report.when == "call" and report.failed:
        pg = (
            item.funcargs.get("authenticated_dashboard")
            or item.funcargs.get("page")
        )
        if pg:
            try:
                allure.attach(
                    pg.screenshot(),
                    name="failure-screenshot",
                    attachment_type=allure.attachment_type.PNG,
                )
            except Exception:
                pass
