"""
DsProfilePage (Bifrost Middleware)
"""
from __future__ import annotations
from playwright.sync_api import expect, Response
from pages.base_page import BasePage

class DsProfilePage(BasePage):
    def click_ds_profile_tab(self, timeout: int = 20000) -> Response:
        """
        cy.intercept("GET", BifrostRoutes.DSProfile).as("dsProfile");
        cy.get(".sidebar").realHover("left").then(() => {
            cy.contains("span", "Middleware").should("be.visible").realHover().click();
        })
        cy.contains("DS Profile").should("be.visible").click();
        cy.wait("@dsProfile", { timeout: 20000 }).its("response.statusCode").should("eq", 200);
        cy.get("table tbody tr").should("have.length.greaterThan", 0);
        """
        import re
        with self.page.expect_response(
            lambda r: "/api/1/middleware/darkstore-profiles/" in r.url and r.request.method == "GET",
            timeout=timeout
        ) as resp_info:
            item = self.page.locator(".sidebar").get_by_text(re.compile(r"^\s*DS Profile\s*$", re.IGNORECASE)).last
            try:
                item.wait_for(state="attached", timeout=2000)
            except Exception:
                self.page.locator("text='Middleware'").first.evaluate("node => node.click()")
                self.page.wait_for_timeout(500)
            
            item.evaluate("node => node.click()")

        expect(self.page.locator("table tbody tr").first).to_be_visible(timeout=15000)
        return resp_info.value
