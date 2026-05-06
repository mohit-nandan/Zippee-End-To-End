from pages.base_page import BasePage


class RulesPage(BasePage):
    HEADING       = ":text('Rules Management')"
    ADD_BTN       = "button:has-text('Add')"
    NAME_SEARCH   = "thead input:nth-of-type(1)"
    DESC_SEARCH   = "thead input:nth-of-type(2)"
    STATUS_SELECT = "thead select, thead [class*='Select']"
    DS_SEARCH     = "thead input:nth-of-type(3)"
    TABLE_ROWS    = "tbody tr"
    RULE_LINKS    = "tbody tr td:first-child a"
    SORT_NAME     = "th:has-text('Name')"

    def is_loaded(self) -> bool:
        try:
            self.expect_visible(self.HEADING, timeout=15000)
            return True
        except Exception:
            return False

    def search_name(self, value: str):
        self.page.locator(self.NAME_SEARCH).fill(value)
        self.wait_for_network_idle()

    def search_description(self, value: str):
        self.page.locator(self.DESC_SEARCH).fill(value)
        self.wait_for_network_idle()

    def filter_status(self, status: str):
        self.page.locator(self.STATUS_SELECT).select_option(label=status)
        self.wait_for_network_idle()

    def click_sort_name(self):
        self.page.locator(self.SORT_NAME).click()
        self.wait_for_spinner_gone()

    def get_row_count(self) -> int:
        return self.page.locator(self.TABLE_ROWS).count()

    def click_rule(self, name: str):
        self.page.locator(f"a:has-text('{name}')").click()
        self.wait_for_network_idle()

    # ── Bifrost / Middleware methods ──────────────────────────────────────────

    def click_rules_tab(self, timeout: int = 20000) -> "Response":
        """
        cy.intercept("GET", BifrostRoutes.Rules).as("rules");
        cy.get(".sidebar").realHover("left").then(() => {
            cy.contains("span", "Middleware").should("be.visible").realHover().click();
        })
        cy.contains("Rules").should("be.visible").click();
        cy.wait("@rules", { timeout: 20000 }).its("response.statusCode").should("eq", 200);
        cy.get("table tbody tr").should("have.length.greaterThan", 0);
        """
        from playwright.sync_api import expect
        import re
        with self.page.expect_response(
            lambda r: "/api/1/middleware/rules/" in r.url and r.request.method == "GET",
            timeout=timeout
        ) as resp_info:
            item = self.page.locator(".sidebar").get_by_text(re.compile(r"^\s*Rules?\s*$", re.IGNORECASE)).last
            try:
                item.wait_for(state="attached", timeout=2000)
            except Exception:
                self.page.locator("text='Middleware'").first.evaluate("node => node.click()")
                self.page.wait_for_timeout(500)
            
            item.evaluate("node => node.click()")

        expect(self.page.locator("table tbody tr").first).to_be_visible(timeout=15000)
        return resp_info.value
