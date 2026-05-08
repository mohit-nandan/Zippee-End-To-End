import re
from playwright.sync_api import Page, expect


class ShipmentLogsPage:
    """Handles /orderLogs/?id={shipment_id} — the Shipment Logs page."""

    def __init__(self, page: Page, base_url: str):
        self.page = page
        self.base_url = base_url.rstrip("/")

    # ── Navigation ─────────────────────────────────────────────────────────────

    def open_logs(self, shipment_id: str):
        """Navigate directly to /orderLogs/?id={shipment_id} and validate the API."""
        with self.page.expect_response(
            lambda r: "/app/api/shipment/logs/" in r.url
                      and f"shipment_id={shipment_id}" in r.url
                      and r.request.method == "GET",
            timeout=30000,
        ) as resp_info:
            self.page.goto(f"{self.base_url}/orderLogs/?id={shipment_id}")
            self.page.wait_for_load_state("domcontentloaded")
        resp = resp_info.value
        assert resp.status == 200, (
            f"shipment/logs API: expected 200, got {resp.status}"
        )
        body = resp.json()
        assert body.get("result") is True, "shipment/logs API: result != true"
        # Wait for heading to confirm page rendered
        self.page.locator("text=Shipment Logs").first.wait_for(
            state="visible", timeout=15000
        )
        return resp

    # ── Assertions ─────────────────────────────────────────────────────────────

    def assert_status_in_logs(self, status: str):
        """Assert that at least one log entry displaying `status` is visible.

        Matches both underscore form (DELIVERY_ATTEMPTED) and space/display form
        (Delivery Attempted) since the UI may humanise the raw status string.
        """
        pattern = re.compile(status.replace("_", "[_ ]"), re.IGNORECASE)
        expect(
            self.page.locator("body").filter(has_text=pattern)
        ).to_be_visible(timeout=10000)

    def assert_log_count_gte(self, minimum: int):
        """Assert the page contains at least `minimum` log timeline entries."""
        # Each log entry has the status text rendered; count distinct status spans
        # The page body contains one entry per override — verified via visible text
        visible_statuses = self.page.locator(
            "span, div, p, h3, h4"
        ).filter(
            has_text=re.compile(
                r"DELIVERED|CANCELLED|RTO|READY|DELIVERY_ATTEMPTED|Allocation Pending",
                re.IGNORECASE,
            )
        )
        count = visible_statuses.count()
        assert count >= minimum, (
            f"Shipment Logs: expected at least {minimum} entries, found {count}"
        )
