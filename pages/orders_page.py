from pages.base_page import BasePage


class OrdersPage(BasePage):
    HEADING          = ":text('Orders')"
    REF_SEARCH       = "thead input:nth-of-type(1)"
    BRAND_SEARCH     = "thead input:nth-of-type(2)"
    PAYMENT_SELECT   = "thead select, thead [class*='Select']"
    DATE_FILTER      = "thead input[placeholder='DD/MM/YYYY']"
    TABLE_ROWS       = "tbody tr"
    ORDER_LINKS      = "tbody tr td:first-child a"
    DATE_FROM        = "input[placeholder*='2026']:first-of-type"

    def is_loaded(self) -> bool:
        try:
            self.expect_visible(self.HEADING, timeout=15000)
            return True
        except Exception:
            return False

    def search_reference(self, ref: str):
        self.page.locator(self.REF_SEARCH).fill(ref)
        self.wait_for_network_idle()

    def search_brand(self, brand: str):
        self.page.locator(self.BRAND_SEARCH).fill(brand)
        self.wait_for_network_idle()

    def filter_payment_mode(self, mode: str):
        sel = self.page.locator("thead").get_by_role("combobox")
        sel.select_option(label=mode)
        self.wait_for_network_idle()

    def click_sort(self, col_text: str):
        self.page.locator(f"th:has-text('{col_text}')").click()
        self.wait_for_spinner_gone()

    def get_row_count(self) -> int:
        return self.page.locator(self.TABLE_ROWS).count()

    def get_first_ref_code(self) -> str:
        return self.page.locator(self.ORDER_LINKS).first.inner_text().strip()

    def click_first_order(self):
        self.page.locator(self.ORDER_LINKS).first.click()
        self.wait_for_network_idle()

    # ── Bifrost / Middleware methods ──────────────────────────────────────────

    def click_order_tab(self, timeout: int = 20000) -> "Response":
        """
        cy.intercept("GET", BifrostRoutes.Order).as("order");
        cy.get(".sidebar").realHover("left").then(() => {
            cy.contains("span", "Middleware").should("be.visible").realHover().click();
        })
        cy.contains("Order").should("be.visible").click();
        cy.wait("@order", { timeout: 20000 }).its("response.statusCode").should("eq", 200);
        cy.get("table tbody tr").should("have.length.greaterThan", 0);
        """
        from playwright.sync_api import expect
        import re
        with self.page.expect_response(
            lambda r: "/api/1/middleware/order/" in r.url and r.request.method == "GET",
            timeout=timeout
        ) as resp_info:
            item = self.page.locator(".sidebar").get_by_text(re.compile(r"^\s*Orders?\s*$", re.IGNORECASE)).last
            try:
                item.wait_for(state="attached", timeout=2000)
            except Exception:
                self.page.locator("text='Middleware'").first.evaluate("node => node.click()")
                self.page.wait_for_timeout(500)
            
            item.evaluate("node => node.click()")

        expect(self.page.locator("table tbody tr").first).to_be_visible(timeout=15000)
        return resp_info.value
