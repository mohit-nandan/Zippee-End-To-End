from pages.base_page import BasePage


class AnalyticsPage(BasePage):
    """
    Mirrors Cypress analytics tab helpers:

        clickOperationTab()  → cy.contains("li:nth-child(1) button:nth-child(1)", "Operation").click()
        clickBusinessTab()   → cy.contains("li:nth-child(2) button:nth-child(1)", "Business").click()
        clickBrandsTab()     → cy.contains("li:nth-child(3) button:nth-child(1)", "Brands").click()
    """

    # Tab buttons — positional selectors matching Cypress li:nth-child(n) button:nth-child(1)
    TAB_OPERATIONS = "li:nth-child(1) button:nth-child(1)"
    TAB_BUSINESS   = "li:nth-child(2) button:nth-child(1)"
    TAB_BRANDS     = "li:nth-child(3) button:nth-child(1)"

    # Expected visible text after each tab loads (from Cypress assertions)
    TEXT_OPERATIONS = "Orders per Day"
    TEXT_BUSINESS   = "Top 5 Brands"
    TEXT_BRANDS     = "Revenue per order"

    def is_loaded(self) -> bool:
        try:
            self.page.wait_for_load_state("domcontentloaded", timeout=10000)
            self.wait_for_spinner_gone(timeout=15000)
            self.expect_visible(self.TAB_OPERATIONS, timeout=15000)
            return True
        except Exception:
            return False

    def click_operations_tab(self):
        """cy.contains("li:nth-child(1) button:nth-child(1)", "Operation").click()"""
        from playwright.sync_api import expect
        tab = self.page.locator(self.TAB_OPERATIONS)
        expect(tab).to_be_visible(timeout=8000)
        tab.click()
        self.wait_for_spinner_gone()
        expect(self.page.locator(f":text('{self.TEXT_OPERATIONS}')").first).to_be_visible(timeout=10000)

    def click_business_tab(self):
        """cy.contains("li:nth-child(2) button:nth-child(1)", "Business").click()"""
        from playwright.sync_api import expect
        tab = self.page.locator(self.TAB_BUSINESS)
        expect(tab).to_be_visible(timeout=8000)
        tab.click()
        self.wait_for_spinner_gone()
        expect(self.page.locator(f":text('{self.TEXT_BUSINESS}')").first).to_be_visible(timeout=10000)

    def click_brands_tab(self):
        """cy.contains("li:nth-child(3) button:nth-child(1)", "Brands").click()"""
        from playwright.sync_api import expect
        tab = self.page.locator(self.TAB_BRANDS)
        expect(tab).to_be_visible(timeout=8000)
        tab.click()
        self.wait_for_spinner_gone()
        expect(self.page.locator(f":text('{self.TEXT_BRANDS}')").first).to_be_visible(timeout=10000)
