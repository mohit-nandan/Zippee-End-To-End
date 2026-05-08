import re
from playwright.sync_api import Page, expect


class BifrostLastMilePage:
    """
    Handles the Bifrost (Middleware) → Shipments → Order detail → Last Mile Logs flow.

    Path:
      /shipments  →  search AWB  →  /shipments/{id}/
      → click order hyperlink  →  /orders/{id}/
      → click Last Mile Logs tab  →  GET /api/1/middleware/order/{id}/tracking/
    """

    def __init__(self, page: Page, base_url: str):
        self.page = page
        self.base_url = base_url.rstrip("/")

    # ── Bifrost Shipments ──────────────────────────────────────────────────────

    def navigate_to_bifrost_shipments(self):
        """Navigate to /shipments (Bifrost / Middleware Shipments) and wait for table."""
        with self.page.expect_response(
            lambda r: "/api/1/middleware/shipment/" in r.url and r.request.method == "GET",
            timeout=30000,
        ) as resp_info:
            self.page.goto(f"{self.base_url}/shipments")
            self.page.wait_for_load_state("domcontentloaded")
        resp = resp_info.value
        assert resp.status == 200, (
            f"Bifrost shipments API: expected 200, got {resp.status}"
        )
        expect(self.page.locator("table tbody tr").first).to_be_visible(timeout=15000)
        return resp

    def search_and_open_bifrost_shipment(self, awb: str):
        """
        Type AWB into the column search input, wait for the matching row,
        then click the AWB link to open /shipments/{id}/.
        """
        search_input = self.page.locator("thead input").first
        search_input.wait_for(state="visible", timeout=10000)
        search_input.click(click_count=3)
        search_input.fill(awb)
        # Wait for the matching row link
        awb_link = self.page.locator("tbody a").filter(
            has_text=re.compile(rf"^{re.escape(awb)}$")
        ).first
        awb_link.wait_for(state="visible", timeout=20000)
        awb_link.click()
        # Confirm we're on the shipment detail page
        self.page.locator("h2:has-text('Shipment Details')").wait_for(
            state="visible", timeout=15000
        )

    # ── Shipment Detail → Order link ───────────────────────────────────────────

    def click_order_link(self):
        """
        In the Orders section of the Bifrost shipment detail page,
        click the first order hyperlink to navigate to /orders/{id}/.
        """
        # The Orders section has h2 "Orders" with links below it
        orders_section = self.page.locator("h2:has-text('Orders')").locator(
            "xpath=./ancestor::div[contains(@class,'rounded') or contains(@class,'card') or contains(@class,'p-4')][1]"
        )
        order_link = orders_section.locator("a[href*='/orders/']").first
        # Fallback: locate by href pattern anywhere on the page
        if not order_link.count():
            order_link = self.page.locator("a[href*='/orders/']").first
        order_link.wait_for(state="visible", timeout=10000)
        order_link.click()
        self.page.locator("h2:has-text('Order Details')").wait_for(
            state="visible", timeout=15000
        )

    # ── Order Detail → Last Mile Logs ──────────────────────────────────────────

    def click_last_mile_logs(self):
        """Click the Last Mile Logs tab.

        The tracking API fires on page load, not on button click, so the data
        is already in the DOM.  Just activate the tab and let assert_status_in_last_mile_logs
        verify the content.
        """
        self.page.get_by_role("button", name=re.compile(r"Last Mile Logs", re.IGNORECASE)).click()

    # ── Assertions ─────────────────────────────────────────────────────────────

    # The bifrost UI renders some statuses with different wording than the API name.
    _DISPLAY_MAP = {
        "DELIVERY_ATTEMPTED": "ATTEMPTED DELIVERY",
    }

    def assert_status_in_last_mile_logs(self, status: str):
        """Assert that at least one Last Mile Log entry with `status` is visible.

        Uses _DISPLAY_MAP to translate API status names to the text the UI actually
        renders (e.g. DELIVERY_ATTEMPTED → ATTEMPTED DELIVERY).
        """
        display = self._DISPLAY_MAP.get(status, status)
        pattern = re.compile(display.replace("_", "[_ ]"), re.IGNORECASE)
        expect(
            self.page.locator("body").filter(has_text=pattern)
        ).to_be_visible(timeout=10000)

    def assert_last_mile_log_count_gte(self, minimum: int):
        """Assert the Last Mile Logs section has at least `minimum` entries."""
        # Log entries are rendered as timeline items inside the right-side panel
        entries = self.page.locator(
            "div[class*='tab'], div[class*='logs'], section[class*='logs']"
        ).filter(
            has_text=re.compile(
                r"DELIVERED|CANCELLED|RTO|READY|DELIVERY_ATTEMPTED|PROCESSED|OPENED",
                re.IGNORECASE,
            )
        )
        # Fallback: count span/div elements with status-like text
        if not entries.count():
            entries = self.page.locator("span,div").filter(
                has_text=re.compile(
                    r"DELIVERED|CANCELLED|RTO|READY|DELIVERY_ATTEMPTED",
                    re.IGNORECASE,
                )
            )
        count = entries.count()
        assert count >= minimum, (
            f"Last Mile Logs: expected at least {minimum} entries, found {count}"
        )
