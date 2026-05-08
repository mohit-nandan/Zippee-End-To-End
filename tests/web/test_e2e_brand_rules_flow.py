"""
E2E Brand Rules Flow — test_11
================================
Flow:
  1. Navigate to /brand → search BRAND_NAME → click brand link.
  2. Click Rules tab.
  3. Click Edit to enter edit mode.
  4. Delete RULE_NAME from draft if already present (idempotency).
  5. Select RULE_NAME from the react-select dropdown → click Preview.
  6. Click Add in the preview panel — rule is appended at the bottom.
  7. Drag the new rule from the bottom to the top (P1).
  8. Click Save → assert API returns result: true.

Configurable constants (change in one place):
    RULE_NAME  — the rule to add (pages/brand_rules_page.py)
    BRAND_NAME — the brand to open (pages/brand_rules_page.py)

Run:
    $env:ENV="preprod"; pytest tests/web/test_e2e_brand_rules_flow.py -v --alluredir=reports/allure-results
"""
import allure
import pytest

from pages.brand_rules_page import BrandRulesPage, RULE_NAME, BRAND_NAME


# ── Module-scoped browser session ─────────────────────────────────────────────

@pytest.fixture(scope="module")
def brand_rules_page(browser_instance, web_cfg):
    """Authenticated browser session shared across all brand-rules test steps."""
    context = browser_instance.new_context(viewport={"width": 1440, "height": 900})
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

    yield BrandRulesPage(pg, base)
    context.close()


# ── Test class ─────────────────────────────────────────────────────────────────

@allure.feature("E2E Brand Rules Flow")
@pytest.mark.e2e
@pytest.mark.web
class TestBrandRulesFlow:
    """
    Full E2E: navigate to brand list → open brand rules → add a rule →
    drag it to the top priority → save.
    """

    @allure.story("11 · Brand Rules — Navigate")
    @allure.title(f"Open '{BRAND_NAME}' brand and navigate to Rules tab")
    def test_11a_navigate_to_rules(self, brand_rules_page, web_cfg):
        with allure.step(f"Navigate to brand list and search '{BRAND_NAME}'"):
            brand_rules_page.navigate_to_brand_list()
            brand_rules_page.search_brand(BRAND_NAME)

        with allure.step(f"Click brand link for '{BRAND_NAME}'"):
            brand_rules_page.click_brand_link(BRAND_NAME)

        with allure.step("Click Rules tab"):
            brand_rules_page.click_rules_tab()

    @allure.story("11 · Brand Rules — Add and Reorder")
    @allure.title(f"Add '{RULE_NAME}' and drag it to top priority")
    def test_11b_add_and_drag_rule(self, brand_rules_page):
        with allure.step("Enter edit mode"):
            brand_rules_page.click_edit_button()

        with allure.step(f"Remove '{RULE_NAME}' if already present (idempotency)"):
            brand_rules_page.delete_rule_if_exists(RULE_NAME)

        with allure.step(f"Select rule '{RULE_NAME}' from dropdown"):
            brand_rules_page.select_rule_from_dropdown(RULE_NAME)

        with allure.step("Click Preview — preview panel opens"):
            brand_rules_page.click_preview()

        with allure.step(f"Click Add — '{RULE_NAME}' appended at bottom of draft table"):
            brand_rules_page.click_add_in_preview_panel(RULE_NAME)

        with allure.step(f"Drag '{RULE_NAME}' to top (P1)"):
            brand_rules_page.drag_last_rule_to_top()
            brand_rules_page.assert_rule_at_position(RULE_NAME, position=1)
            allure.dynamic.parameter("rule_name", RULE_NAME)

    @allure.story("11 · Brand Rules — Save")
    @allure.title("Save draft rules and confirm API success")
    def test_11c_save_rules(self, brand_rules_page):
        with allure.step("Click Save and validate API response"):
            resp = brand_rules_page.click_save()
            body = resp.json()
            assert body.get("result") is True, f"Save API result != true: {body}"
            allure.dynamic.parameter("api_status", resp.status)
            allure.dynamic.parameter("api_result", body.get("result"))
