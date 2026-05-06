"""
BrandDetailPage
===============
Page object for the brand detail view (reached by clicking a brand row link).

Mirrors the Cypress helper pattern::

    switchTab(tabName, route, expectedText) {
        cy.intercept("GET", route).as(alias);
        cy.contains("li", tabName).should("be.visible").click();
        cy.wait(`@${alias}`);
        cy.contains(expectedText).should("be.visible");
    }

Each `switch_tab()` call:
    1. Sets up a Playwright response waiter for the API URL pattern (intercept).
    2. Finds the <li> that contains `tab_name` and clicks it.
    3. Waits for the API response and returns it so the caller can validate.
    4. Asserts that `expected_text` is visible on the page.
"""
from __future__ import annotations

from playwright.sync_api import Page, expect, Response

from pages.base_page import BasePage


class BrandDetailPage(BasePage):
    # ── Common selectors ──────────────────────────────────────────────────────
    TAB_NAV = "li"          # Cypress: cy.contains("li", tabName)

    # ── Tab labels (match the UI text exactly) ────────────────────────────────
    TAB_COMMERCIALS   = "Commercials"
    TAB_GST           = "GST Details"
    TAB_WAREHOUSES    = "Warehouses"
    TAB_WEBHOOKS      = "Webhooks"
    TAB_RULES         = "Rules"
    TAB_COMMS         = "Comms"
    TAB_CONFIGURATION = "Configuration"

    # ── Visible text that should appear after each tab loads ──────────────────
    TEXT_COMMERCIALS   = "Commercials"
    TEXT_GST           = "GST Details"
    TEXT_WAREHOUSES    = "Warehouses"
    TEXT_WEBHOOKS      = "Webhooks"
    TEXT_RULES         = "Rules"
    TEXT_COMMS         = "WhatsApp Communications"
    TEXT_CONFIGURATION = "Standard Delivery"

    # ──────────────────────────────────────────────────────────────────────────
    # Core helper — mirrors Cypress switchTab()
    # ──────────────────────────────────────────────────────────────────────────

    def switch_tab(
        self,
        tab_name: str,
        api_url_fragment: str,
        expected_text: str,
        timeout: int = 15000,
    ) -> Response:
        """
        Playwright equivalent of Cypress switchTab().

        Args:
            tab_name:         Exact text of the <li> tab to click.
            api_url_fragment: Substring matched against the GET request URL.
            expected_text:    Text that must be visible after the tab loads.
            timeout:          Max ms to wait for the API response.

        Returns:
            The Playwright Response object so callers can validate the body.
        """
        with self.page.expect_response(
            lambda r: api_url_fragment in r.url and r.request.method == "GET" and r.status == 200,
            timeout=timeout,
        ) as resp_info:
            # cy.contains("li", tabName).should("be.visible").click()
            tab_locator = self.page.locator(f"li:has-text('{tab_name}')").first
            expect(tab_locator).to_be_visible(timeout=8000)
            tab_locator.click()

        self.wait_for_spinner_gone()
        # cy.contains(expectedText).should("be.visible")
        expect(self.page.locator(f":text('{expected_text}')").first).to_be_visible(timeout=8000)
        return resp_info.value

    # ──────────────────────────────────────────────────────────────────────────
    # Individual tab helpers — match Cypress clickCommercialsTab() etc.
    # ──────────────────────────────────────────────────────────────────────────

    def click_commercials_tab(self, api_fragment: str) -> Response:
        return self.switch_tab(self.TAB_COMMERCIALS, api_fragment, self.TEXT_COMMERCIALS)

    def click_gst_details_tab(self, api_fragment: str) -> Response:
        return self.switch_tab(self.TAB_GST, api_fragment, self.TEXT_GST)

    def click_warehouses_tab(self, api_fragment: str) -> Response:
        return self.switch_tab(self.TAB_WAREHOUSES, api_fragment, self.TEXT_WAREHOUSES)

    def click_webhooks_tab(self, api_fragment: str) -> Response:
        return self.switch_tab(self.TAB_WEBHOOKS, api_fragment, self.TEXT_WEBHOOKS)

    def click_rules_tab(self, api_fragment: str) -> Response:
        # Cypress: cy.contains("li", "Rules").should("be.visible").click()
        return self.switch_tab(self.TAB_RULES, api_fragment, self.TEXT_RULES)

    def click_comms_tab(self, api_fragment: str) -> Response:
        return self.switch_tab(self.TAB_COMMS, api_fragment, self.TEXT_COMMS)

    def click_configuration_tab(self, api_fragment: str) -> Response:
        return self.switch_tab(self.TAB_CONFIGURATION, api_fragment, self.TEXT_CONFIGURATION)
