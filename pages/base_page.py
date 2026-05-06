"""
BasePage — all page objects inherit from this.
Uses Playwright's built-in expect() for auto-retry assertions (no manual sleep/poll).
"""
import re
import allure
from playwright.sync_api import Page, expect, Locator


class BasePage:
    # Override in subclasses if the page has a different loading indicator
    SPINNER = "[class*='loading'], [class*='spinner'], .animate-spin"

    def __init__(self, page: Page):
        self.page = page

    # ── Navigation ────────────────────────────────────────────────────────────

    def navigate(self, url: str):
        with allure.step(f"Navigate to {url}"):
            self.page.goto(url)
            self.page.wait_for_load_state("domcontentloaded")

    def current_url(self) -> str:
        return self.page.url

    def go_to(self, section: str, base_url: str):
        from pages.nav_page import NavPage
        NavPage(self.page).go_to(section, base_url)

    # ── Waits ─────────────────────────────────────────────────────────────────

    def wait_for_network_idle(self, timeout: int = 3000):
        # React SPAs never reach networkidle due to background polling.
        # Short debounce + spinner wait is a reliable alternative.
        self.page.wait_for_timeout(500)
        self.wait_for_spinner_gone(timeout=timeout)

    def wait_for_spinner_gone(self, timeout: int = 15000):
        try:
            self.page.locator(self.SPINNER).first.wait_for(state="hidden", timeout=timeout)
        except Exception:
            pass  # spinner may never appear — that's fine

    def wait_for_selector(self, selector: str, timeout: int = 10000):
        self.page.locator(selector).wait_for(state="visible", timeout=timeout)

    def wait_for_url_contains(self, path: str, timeout: int = 10000):
        self.page.wait_for_url(f"**{path}**", timeout=timeout)

    # ── Locator helpers (raw, use sparingly — prefer expect()) ───────────────

    def locator(self, selector: str) -> Locator:
        return self.page.locator(selector)

    def fill(self, selector: str, value: str):
        self.page.locator(selector).fill(value)

    def clear_and_fill(self, selector: str, value: str):
        loc = self.page.locator(selector)
        loc.clear()
        loc.fill(value)

    def click(self, selector: str):
        self.page.locator(selector).click()

    def get_text(self, selector: str) -> str:
        return self.page.locator(selector).inner_text()

    def get_all_texts(self, selector: str) -> list[str]:
        return self.page.locator(selector).all_inner_texts()

    def count(self, selector: str) -> int:
        return self.page.locator(selector).count()

    def is_visible(self, selector: str) -> bool:
        return self.page.locator(selector).is_visible()

    # ── Playwright expect() assertions (auto-retry, failure-friendly) ─────────

    def expect_visible(self, selector: str, timeout: int = 10000):
        expect(self.page.locator(selector)).to_be_visible(timeout=timeout)

    def expect_hidden(self, selector: str, timeout: int = 10000):
        expect(self.page.locator(selector)).to_be_hidden(timeout=timeout)

    def expect_text(self, selector: str, text: str, timeout: int = 10000):
        expect(self.page.locator(selector)).to_contain_text(text, timeout=timeout)

    def expect_url(self, path: str, timeout: int = 10000):
        # Regex so trailing slash is optional: matches /brand and /brand/
        normalized = path.rstrip("/")
        expect(self.page).to_have_url(re.compile(re.escape(normalized) + r"/?$"), timeout=timeout)

    def expect_row_count(self, count: int, row_selector: str = "tbody tr", timeout: int = 8000):
        """Auto-retrying row count assertion — safe for async React table updates."""
        expect(self.page.locator(row_selector)).to_have_count(count, timeout=timeout)

    def expect_count_gte(self, selector: str, minimum: int):
        count = self.page.locator(selector).count()
        assert count >= minimum, (
            f"Expected at least {minimum} elements matching '{selector}', found {count}"
        )

    # ── Table helpers ─────────────────────────────────────────────────────────

    def get_table_row_count(self, row_selector: str = "tbody tr") -> int:
        return self.page.locator(row_selector).count()

    def get_column_values(self, col_index: int, row_sel: str = "tbody tr") -> list[str]:
        rows = self.page.locator(row_sel)
        values = []
        for i in range(rows.count()):
            try:
                values.append(rows.nth(i).locator("td").nth(col_index).inner_text().strip())
            except Exception:
                pass
        return values

    # ── Screenshot ────────────────────────────────────────────────────────────

    def take_screenshot(self, name: str = "screenshot"):
        data = self.page.screenshot()
        allure.attach(data, name=name, attachment_type=allure.attachment_type.PNG)
        return data
