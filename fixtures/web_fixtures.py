import os
import pytest
import allure
from playwright.sync_api import sync_playwright
from utils.config_loader import get_config


@pytest.fixture(scope="session")
def browser_instance():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        yield browser
        browser.close()


@pytest.fixture
def page(browser_instance):
    context = browser_instance.new_context()
    page = context.new_page()
    yield page
    context.close()


@pytest.fixture
def authenticated_dashboard(page):
    cfg = get_config()
    page.goto(cfg["dashboard_url"] + "/login")
    page.wait_for_load_state("networkidle")
    page.locator("input[name='email']").fill(os.environ["DASHBOARD_USER"])
    page.locator("input[name='password']").fill(os.environ["DASHBOARD_PASSWORD"])
    page.locator("button[type='submit']").click()
    page.wait_for_load_state("networkidle")
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
                allure.attach(screenshot, name="failure-screenshot", attachment_type=allure.attachment_type.PNG)
            except Exception:
                pass
