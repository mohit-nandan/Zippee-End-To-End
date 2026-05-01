import os
import pytest
import allure
from playwright.sync_api import sync_playwright
from utils.config_loader import get_config


@pytest.fixture(scope="session")
def browser_instance():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=["--no-sandbox"])
        yield browser
        browser.close()


@pytest.fixture(scope="session")
def web_cfg():
    env = os.getenv("ENV", "preprod")
    return get_config(env)


@pytest.fixture
def page(browser_instance):
    context = browser_instance.new_context(viewport={"width": 1440, "height": 900})
    page = context.new_page()
    yield page
    context.close()


@pytest.fixture
def authenticated_dashboard(page, web_cfg):
    """Logs in and yields a fully authenticated Playwright page."""
    base = web_cfg["dashboard_url"].rstrip("/")
    page.goto(f"{base}/sign-in")
    page.wait_for_load_state("networkidle")

    # Step 1 — enter email and continue
    page.locator("#email").fill(web_cfg["admin_user"])
    page.get_by_role("button", name="Continue with Email").click()
    page.locator("input[type='password']").wait_for(state="visible", timeout=8000)

    # Step 2 — enter password and login
    page.locator("input[type='password']").fill(web_cfg["admin_pass"])
    page.get_by_role("button", name="Login", exact=True).click()
    page.wait_for_load_state("networkidle")
    page.wait_for_url(f"{base}/", timeout=15000)

    yield page


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    if report.when == "call" and report.failed:
        page = item.funcargs.get("page") or item.funcargs.get("authenticated_dashboard")
        if page:
            try:
                screenshot = page.screenshot()
                allure.attach(screenshot, name="failure-screenshot",
                              attachment_type=allure.attachment_type.PNG)
            except Exception:
                pass
