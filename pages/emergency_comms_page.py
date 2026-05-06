"""
EmergencyCommsPage
==================
Mirrors Cypress EmergencyCommsPage:

    clickEmergencyCommsTab()
        cy.contains("a", "Emergency Comms").click()

    clickCommsLogsTab()
        cy.intercept("GET", BaseRoutes.CommsLogs).as("commsLogs")
        cy.contains("button", "View Logs").click()
        cy.wait("@commsLogs")
        cy.contains("Communication Upload Logs").should("be.visible")
"""
from __future__ import annotations

from playwright.sync_api import expect, Response

from pages.base_page import BasePage


class EmergencyCommsPage(BasePage):

    # ── Selectors ─────────────────────────────────────────────────────────────
    # cy.contains("a", "Emergency Comms")
    NAV_LINK        = "a:has-text('Emergency Comms')"

    # cy.contains("button", "View Logs")
    VIEW_LOGS_BTN   = "button:has-text('View Logs')"

    # cy.contains("Communication Upload Logs").should("be.visible")
    LOGS_HEADING    = ":text('Communication Upload Logs')"

    # API URL fragment for cy.intercept("GET", BaseRoutes.CommsLogs)
    COMMS_LOGS_API  = "/api/1/comms-logs/"

    # ── Page load check ───────────────────────────────────────────────────────

    def is_loaded(self) -> bool:
        try:
            self.page.wait_for_load_state("domcontentloaded", timeout=10000)
            self.wait_for_spinner_gone(timeout=15000)
            # "View Logs" button is the key element on the Emergency Comms page
            self.expect_visible(self.VIEW_LOGS_BTN, timeout=15000)
            return True
        except Exception:
            return False

    # ── Actions ───────────────────────────────────────────────────────────────

    def click_comms_logs_tab(self, timeout: int = 15000) -> Response:
        """
        Mirrors Cypress clickCommsLogsTab():
            cy.intercept("GET", BaseRoutes.CommsLogs).as("commsLogs")
            cy.contains("button", "View Logs").click()
            cy.wait("@commsLogs")
            cy.contains("Communication Upload Logs").should("be.visible")

        Returns the API Response so the caller can validate the body.
        """
        with self.page.expect_response(
            lambda r: self.COMMS_LOGS_API in r.url
                      and r.request.method == "GET"
                      and r.status == 200,
            timeout=timeout,
        ) as resp_info:
            btn = self.page.locator(self.VIEW_LOGS_BTN)
            expect(btn).to_be_visible(timeout=8000)
            btn.click()

        self.wait_for_spinner_gone()
        # cy.contains("Communication Upload Logs").should("be.visible")
        expect(self.page.locator(self.LOGS_HEADING).first).to_be_visible(timeout=10000)
        return resp_info.value
