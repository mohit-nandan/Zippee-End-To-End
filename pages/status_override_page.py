import re
from playwright.sync_api import Page, expect, TimeoutError as PlaywrightTimeoutError


# Statuses the user can override to (PICKUP_ATTEMPTED is excluded per spec)
OVERRIDE_STATUSES = ["CANCELLED", "RTO", "READY", "DELIVERY_ATTEMPTED"]
DEFAULT_REASON = "Customer Unavailable"


class StatusOverridePage:
    def __init__(self, page: Page):
        self.page = page

    # ── Navigation ─────────────────────────────────────────────────────────────

    def navigate_to_all_shipments(self, base_url: str):
        """Navigate to /pnd/shipments and activate the All Shipments filter tab."""
        self.page.goto(f"{base_url.rstrip('/')}/pnd/shipments")
        self.page.wait_for_load_state("domcontentloaded")
        self.page.locator("table").first.wait_for(state="visible", timeout=20000)
        with self.page.expect_response(
            lambda r: "/app/api/shipments/" in r.url and r.request.method == "POST",
            timeout=30000,
        ) as resp_info:
            self.page.locator("div.cursor-pointer").filter(
                has_text=re.compile(r"^\s*All Shipments\s*$")
            ).first.click()
        resp = resp_info.value
        assert resp.status == 200, f"All Shipments API: expected 200, got {resp.status}"
        return resp

    def _table(self):
        """The All Shipments table — uniquely identified by its Shipment Status column."""
        return self.page.locator("table").filter(has_text="Shipment Status")

    def _panel(self):
        """Locator scoped to the Override Status slide-in panel."""
        return self.page.locator("h2:has-text('Override Status')").locator(
            "xpath=ancestor::div[.//button[normalize-space(.)='Update']][1]"
        )

    # ── AWB search ─────────────────────────────────────────────────────────────

    def search_awb(self, awb: str, timeout: int = 20000):
        """Fill the AWB column search input and wait for the row to appear."""
        table = self._table()
        search_input = table.locator("thead input[type='search']").first
        search_input.wait_for(state="visible", timeout=10000)
        search_input.fill(awb)
        table.locator("tbody a").filter(
            has_text=re.compile(rf"^{re.escape(awb)}$")
        ).first.wait_for(state="visible", timeout=timeout)

    def get_pnd_shipment_id(self, awb: str) -> str:
        """Return the internal PND shipment ID extracted from the AWB link href."""
        href = self._table().locator("tbody a").filter(
            has_text=re.compile(rf"^{re.escape(awb)}$")
        ).first.get_attribute("href")
        return href.rstrip("/").split("/")[-1]

    # ── Override modal interaction ─────────────────────────────────────────────

    def open_override_modal(self, awb: str):
        """On the row containing AWB, click the 3-dot button → Override Status."""
        row = self._table().locator("tr[role='button']").filter(
            has_text=re.compile(re.escape(awb))
        ).first
        row.locator("td.sticky button[type='button']").click()
        self.page.locator("div.dropdown-menu").wait_for(state="visible", timeout=5000)
        self.page.locator("div.dropdown-menu button").filter(
            has_text=re.compile(r"Override Status", re.IGNORECASE)
        ).click()
        self.page.locator("h2:has-text('Override Status')").wait_for(
            state="visible", timeout=10000
        )
        # Wait until the panel's react-select input is interactive before returning
        self._panel().locator("input[id^='react-select']").wait_for(
            state="visible", timeout=10000
        )

    def select_status(self, status: str):
        """Select a status from the React Select dropdown in the modal."""
        panel = self._panel()
        # Scope the input lookup to the panel to avoid ambiguity with table filters
        react_input = panel.locator("input[id^='react-select']")
        react_input.click()
        # Options render into a portal (outside the panel); match globally by text
        option = self.page.locator("[id^='react-select'][id*='-option']").filter(
            has_text=re.compile(rf"^{re.escape(status)}$", re.IGNORECASE)
        ).first
        option.wait_for(state="visible", timeout=5000)
        option.click()

    def select_reason(self, reason: str = DEFAULT_REASON):
        """Click the reason label to fire React's synthetic onClick on the radio.

        React registers onChange via a delegated click on the <label>, not a
        native change event on the <input>.  Clicking the label element directly
        (rather than calling .check() on the nested input) is the only approach
        that reliably fires the synthetic event and updates component state.
        """
        panel = self._panel()
        label = panel.locator("label").filter(
            has_text=re.compile(rf"^\s*{re.escape(reason)}\s*$", re.IGNORECASE)
        ).first
        label.scroll_into_view_if_needed()
        label.click()
        # Verify the underlying radio is now checked (confirms React state updated)
        expect(label.locator("input[type='radio']")).to_be_checked(timeout=3000)

    def submit_override(self, status: str = ""):
        """Click Update, wait for the override API call, then wait for the panel to close."""
        heading = self.page.locator("h2:has-text('Override Status')")
        try:
            with self.page.expect_response(
                lambda r: "valkyrie/status" in r.url,
                timeout=15000,
            ) as resp_info:
                heading.locator(
                    "xpath=ancestor::div"
                    "[.//button[normalize-space(.)='Update']]"
                    "[1]"
                    "//button[normalize-space(.)='Update']"
                ).click()
        except PlaywrightTimeoutError:
            raise AssertionError(
                f"Override API (valkyrie/status) was never called for status={status!r}. "
                f"The Update click did not trigger a network request — "
                f"likely status or reason is not set in React state."
            ) from None

        resp = resp_info.value
        try:
            body = resp.json()
        except Exception:
            body = {}
        assert resp.status < 400 and body.get("result"), (
            f"Override API rejected for status={status!r}: "
            f"HTTP {resp.status} — {body.get('message', body)}"
        )
        # The panel does not auto-close after a successful update and cannot be
        # dismissed programmatically (X button does not respond to synthetic events).
        # The caller always navigates away immediately after this call (logs page,
        # bifrost, or All Shipments), which destroys the panel via page.goto().

    # ── Convenience: full override in one call ─────────────────────────────────

    def override_to_status(
        self,
        awb: str,
        status: str,
        reason: str = DEFAULT_REASON,
    ):
        """Open override modal for AWB, select status + reason, submit."""
        self.open_override_modal(awb)
        self.select_status(status)
        self.select_reason(reason)
        self.submit_override(status=status)
