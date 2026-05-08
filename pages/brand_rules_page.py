import re
from playwright.sync_api import Page, expect

# Configurable constants — change RULE_NAME to test a different rule
RULE_NAME = "preprod_expresshub_test"
BRAND_NAME = "testing_fabbox"


class BrandRulesPage:
    def __init__(self, page: Page, base_url: str):
        self.page = page
        self.base_url = base_url.rstrip("/")

    # ── Navigation ──────────────────────────────────────────────────────────────

    def navigate_to_brand_list(self):
        """Navigate to /brand and wait for the brands table to load."""
        self.page.goto(f"{self.base_url}/brand")
        self.page.wait_for_load_state("domcontentloaded")
        self.page.locator("table tbody tr").first.wait_for(state="visible", timeout=15000)

    def search_brand(self, brand_name: str):
        """Type brand_name into the table column search input and wait for matching row."""
        search_input = self.page.locator("thead input").first
        search_input.wait_for(state="visible", timeout=10000)
        search_input.click(click_count=3)
        search_input.fill(brand_name)
        self.page.locator("tbody a").filter(
            has_text=re.compile(re.escape(brand_name), re.IGNORECASE)
        ).first.wait_for(state="visible", timeout=15000)

    def click_brand_link(self, brand_name: str):
        """Click the brand link in the filtered table row."""
        self.page.locator("tbody a").filter(
            has_text=re.compile(re.escape(brand_name), re.IGNORECASE)
        ).first.click()
        self.page.wait_for_load_state("domcontentloaded")

    def click_rules_tab(self):
        """Click the Rules tab on the brand detail page and wait for Brand Rules section."""
        self.page.get_by_role("button", name="Rules").click()
        self.page.locator("h2:has-text('Brand Rules')").wait_for(state="visible", timeout=10000)

    # ── Edit mode ───────────────────────────────────────────────────────────────

    def click_edit_button(self):
        """Enter edit mode — Cancel/Save/Apply buttons appear after this call."""
        self.page.get_by_role("button", name="Edit").click()
        self.page.get_by_role("button", name="Cancel").wait_for(state="visible", timeout=10000)

    def delete_rule_if_exists(self, rule_name: str):
        """
        Remove rule_name from the draft Brand Rules table if it is present.
        Must be called in edit mode (Delete buttons are only visible after click_edit_button).
        """
        row = self.page.locator("table tbody tr").filter(
            has_text=re.compile(re.escape(rule_name), re.IGNORECASE)
        ).first
        if row.count() == 0:
            return
        delete_btn = row.get_by_role("button", name="Delete Rule")
        if delete_btn.is_visible():
            delete_btn.click()

    # ── Rule selection and preview ──────────────────────────────────────────────

    def select_rule_from_dropdown(self, rule_name: str):
        """Type rule_name into the react-select input and click the matching option."""
        react_input = self.page.locator("input[id^='react-select']").first
        react_input.click()
        react_input.fill(rule_name)
        option = self.page.locator("[id^='react-select'][id*='-option']").filter(
            has_text=re.compile(rf"^{re.escape(rule_name)}$", re.IGNORECASE)
        ).first
        option.wait_for(state="visible", timeout=5000)
        option.click()

    def click_preview(self):
        """Click the main Preview button (exact match to avoid hitting per-row 'Preview Rule' buttons)."""
        self.page.get_by_role("button", name="Preview", exact=True).click()
        self.page.get_by_role("button", name="Add").wait_for(state="visible", timeout=10000)

    def click_add_in_preview_panel(self, rule_name: str):
        """
        Click Add in the preview panel.
        Waits for a new 'Drag to reorder' handle to appear, confirming the rule
        was appended to the draft table and the panel was dismissed.
        """
        drag_count_before = self.page.get_by_role("button", name="Drag to reorder").count()
        self.page.get_by_role("button", name="Add").click()
        expect(
            self.page.get_by_role("button", name="Drag to reorder").nth(drag_count_before)
        ).to_be_visible(timeout=10000)

    # ── Drag-to-reorder ────────────────────────────────────────────────────────

    def drag_last_rule_to_top(self):
        """Drag the bottom-most rule row to the first position in the draft table."""
        drag_buttons = self.page.get_by_role("button", name="Drag to reorder")
        count = drag_buttons.count()
        assert count >= 2, f"Expected at least 2 drag handles, found {count}"
        drag_buttons.nth(count - 1).drag_to(drag_buttons.first)

    def assert_rule_at_position(self, rule_name: str, position: int = 1):
        """Assert rule_name occupies the given priority position (1-based)."""
        target_row = self.page.locator("table tbody tr").nth(position - 1)
        expect(target_row).to_contain_text(rule_name, timeout=5000)

    # ── Save ────────────────────────────────────────────────────────────────────

    def click_save(self):
        """Click Save and assert the save API returns result: true."""
        with self.page.expect_response(
            lambda r: "/api/1/brands/" in r.url
                      and "/rules/" in r.url
                      and r.request.method == "POST",
            timeout=15000,
        ) as resp_info:
            self.page.get_by_role("button", name="Save").click()
        resp = resp_info.value
        body = resp.json()
        assert resp.status < 400 and body.get("result"), (
            f"Brand rules Save API failed: HTTP {resp.status} — {body}"
        )
        return resp
