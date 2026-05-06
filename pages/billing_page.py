"""
BillingPage
===========
Playwright translation of Cypress BillingPage:

    clickBillingTab()           → POST /api/1/transactionHome/      → status 200
    clickDatepicker()           → POST /api/1/transactionHeader/     → status 200 + Total Usage > 0
    clickDeductionsDetailsTab() → POST /api/1/transactionHistory/    → status 200 + rows > 0
    clickInvoiceHistoryTab()    → POST /api/1/invoice/history/       → status 200
"""
from __future__ import annotations

from playwright.sync_api import expect, Response

from pages.base_page import BasePage


class BillingPage(BasePage):

    # ── Selectors ─────────────────────────────────────────────────────────────
    HEADING             = ":text('Billing & Invoices')"

    # cy.contains("li", "Invoices")  — tab in the top nav
    TAB_DEDUCTIONS      = "li:has-text('Deductions')"
    TAB_INVOICES        = "li:has-text('Invoices')"

    # stat card labels
    STAT_TOTAL_USAGE    = ":text('Total Usage')"
    STAT_GENERAL_USAGE  = ":text('General Usage')"
    STAT_NUM_DEDUCTIONS = ":text('No. of Deductions')"

    # cy.contains("Deduction View") sub-tab button
    SUBTAB_DEDUCTION    = "button:has-text('Deduction View'), :text('Deduction View')"
    SUBTAB_DAILY        = "button:has-text('Daily Summary'), :text('Daily Summary')"

    # cy.get(".relative.inline-block") — date picker trigger
    DATE_PICKER_TRIGGER = ".relative.inline-block"
    LAST_MONTH_OPTION   = ".rdrDefinedRangesWrapper :text('Last Month')"

    # table
    TABLE_ROWS          = "tbody tr"

    # action buttons (kept for visibility checks)
    GEN_INVOICE_BTN     = "button:has-text('Generate Invoice')"
    SEND_INVOICES_BTN   = "button:has-text('Send Invoices')"
    MG_ADJUSTMENT_BTN   = "button:has-text('MG Adjustment')"

    # ── API URL fragments (POST) ───────────────────────────────────────────────
    API_TRANSACTION_HOME    = "/api/1/transactionHome/"
    API_TRANSACTION_HEADER  = "/api/1/transactionHeader/"
    API_TRANSACTION_HISTORY = "/api/1/transactionHistory/"
    API_INVOICE_HISTORY     = "/api/1/invoice/history/"

    # ── Page load ─────────────────────────────────────────────────────────────

    def is_loaded(self) -> bool:
        try:
            self.page.wait_for_load_state("domcontentloaded", timeout=10000)
            self.wait_for_spinner_gone(timeout=15000)
            self.expect_visible(self.TAB_DEDUCTIONS, timeout=15000)
            return True
        except Exception:
            return False

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _wait_post(self, api_fragment: str, timeout: int = 20000):
        """Return a context manager that waits for a POST response matching api_fragment."""
        return self.page.expect_response(
            lambda r: api_fragment in r.url
                      and r.request.method == "POST"
                      and r.status == 200,
            timeout=timeout,
        )

    # ── Cypress method translations ────────────────────────────────────────────

    def click_billing_tab(self, timeout: int = 20000) -> Response:
        """
        cy.intercept("POST", BillingRoutes.GetBillingDetails).as("transactionHome")
        cy.contains("a", "Billing").click()
        cy.wait("@transactionHome").its("response.statusCode").should("eq", 200)

        NOTE: navigation already happens via go_to("billing") — this method
        intercepts the transactionHome call that fires on page load and
        returns the response for validation.
        """
        with self._wait_post(self.API_TRANSACTION_HOME, timeout) as resp_info:
            # Trigger the call by navigating (caller should call go_to first,
            # but if already on page, reload to fire the POST)
            self.page.reload()
            self.wait_for_spinner_gone()
        return resp_info.value

    def click_datepicker(self, timeout: int = 20000) -> Response:
        """
        cy.intercept("POST", BillingRoutes.GetBillingHeader).as("billingHeader")
        cy.get(".relative.inline-block").click()
        cy.get(".rdrDefinedRangesWrapper").contains("Last Month").click()
        cy.wait("@billingHeader").its("response.statusCode").should("eq", 200)
        cy.contains("p", "Total Usage")...find("p.text-2xl")...value > 0
        """
        with self._wait_post(self.API_TRANSACTION_HEADER, timeout) as resp_info:
            self.page.locator(self.DATE_PICKER_TRIGGER).first.click()
            expect(self.page.locator(self.LAST_MONTH_OPTION)).to_be_visible(timeout=8000)
            self.page.locator(self.LAST_MONTH_OPTION).click()
            self.wait_for_spinner_gone()
        return resp_info.value

    def click_deductions_details_tab(self, timeout: int = 20000) -> Response:
        """
        cy.intercept("POST", BillingRoutes.GetTransactionHistory).as("transactionHistory")
        cy.contains("Deduction View").click()
        cy.wait("@transactionHistory").its("response.statusCode").should("eq", 200)
        cy.get("table tbody tr").should("have.length.greaterThan", 0)
        """
        with self._wait_post(self.API_TRANSACTION_HISTORY, timeout) as resp_info:
            btn = self.page.locator(self.SUBTAB_DEDUCTION).first
            expect(btn).to_be_visible(timeout=8000)
            btn.click()
            self.wait_for_spinner_gone()
        return resp_info.value

    def click_invoice_history_tab(self, timeout: int = 20000) -> Response:
        """
        cy.intercept("POST", BillingRoutes.GetInoviceHistory).as("invoiceHistory")
        cy.contains("li", "Invoices").click()
        cy.wait("@invoiceHistory").its("response.statusCode").should("eq", 200)
        cy.get("table tbody tr").should("have.length.greaterThan", 0)
        """
        with self._wait_post(self.API_INVOICE_HISTORY, timeout) as resp_info:
            tab = self.page.locator(self.TAB_INVOICES).first
            expect(tab).to_be_visible(timeout=8000)
            tab.click()
            self.wait_for_spinner_gone()
        return resp_info.value

    # ── Utility ───────────────────────────────────────────────────────────────

    def get_row_count(self) -> int:
        return self.page.locator(self.TABLE_ROWS).count()

    def stats_visible(self) -> bool:
        return (
            self.is_visible(self.STAT_TOTAL_USAGE) and
            self.is_visible(self.STAT_GENERAL_USAGE)
        )
