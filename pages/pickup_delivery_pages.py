import re
from playwright.sync_api import Page, expect


def _ensure_pd_visible(page, item_locator):
    """Hover sidebar to expand it, then expand Pickup Delivery accordion if collapsed."""
    page.locator(".sidebar").hover()
    try:
        item_locator.wait_for(state="visible", timeout=2000)
    except Exception:
        page.locator(".sidebar").get_by_role("button").filter(
            has_text=re.compile(r"Pickup Delivery", re.IGNORECASE)
        ).first.click()
        item_locator.wait_for(state="visible", timeout=8000)


# ── Deliveries → Shipments ────────────────────────────────────────────────────

SHIPMENT_HEADERS = [
    "Type", "AWB Number", "Order Number", "Brand Name", "Shipment Status",
    "Rider", "Delivery Pincode", "Delivery Address", "Total Value",
    "Payment Mode", "Customer Name", "Customer Mobile", "Delivery Start",
    "Delivery End", "Pickup Address", "Pickup Pincode", "No. Of Attempt",
    "Darkstore", "Trip ID", "Item Count", "Order Created By", "Meta Tags",
]

SHIPMENT_FILTER_TABS = [
    "Assign Now", "Assign Later", "Assigned", "Completed", "Return", "All Shipments"
]


class DeliveriesShipmentsPage:
    def __init__(self, page: Page):
        self.page = page

    def click_deliveries_tab(self):
        """Click Deliveries sidebar item → validates shipments API + all table headers."""
        with self.page.expect_response(
            lambda r: "/app/api/shipments/" in r.url and r.request.method == "POST",
            timeout=30000,
        ) as resp_info:
            item = self.page.locator(".sidebar").get_by_text(
                re.compile(r"^\s*Deliveries\s*$", re.IGNORECASE)
            ).last
            _ensure_pd_visible(self.page, item)
            item.click()
        resp = resp_info.value
        assert resp.status == 200, f"shipments API: expected 200, got {resp.status}"
        body = resp.json()
        assert body.get("result") is True, "shipments API: result != true"
        expect(self.page.locator("table thead").first).to_be_visible(timeout=15000)
        self._assert_shipment_headers()
        return resp

    def click_shipment_filter_tab(self, tab: str):
        """Click a Shipments status filter tab and validate API response."""
        with self.page.expect_response(
            lambda r: "/app/api/shipments/" in r.url and r.request.method == "POST",
            timeout=30000,
        ) as resp_info:
            self.page.locator("div.flex-1.min-w-max, div.cursor-pointer").filter(
                has_text=re.compile(rf"^\s*{re.escape(tab)}\s*$")
            ).first.click()
        resp = resp_info.value
        assert resp.status == 200, f"shipments [{tab}] API: expected 200, got {resp.status}"
        body = resp.json()
        assert body.get("result") is True, f"shipments [{tab}] API: result != true"
        return resp

    def _assert_shipment_headers(self):
        for header in SHIPMENT_HEADERS:
            expect(
                self.page.locator(f"th:has-text('{header}')").first
            ).to_be_visible(timeout=5000)


# ── Deliveries → Trips ────────────────────────────────────────────────────────

TRIP_HEADERS = [
    "Trip ID", "Trip Status", "Rider", "Rider Contact",
    "No. Of Shipments", "Total Shipment Value",
    "Created Date", "Updated Date", "Completed Date", "Action",
]

TRIP_FILTER_TABS = ["Draft", "Created", "Ongoing", "Completed", "All"]


class DeliveriesTripsPage:
    def __init__(self, page: Page):
        self.page = page

    def click_trips_tab(self):
        """Click the Trips tab → validates trip API (Draft default) + all table headers."""
        with self.page.expect_response(
            lambda r: "/app/api/trip/" in r.url and r.request.method == "POST",
            timeout=30000,
        ) as resp_info:
            self.page.get_by_role("button", name=re.compile(r"^\s*Trips\s*$")).first.click()
        resp = resp_info.value
        assert resp.status == 200, f"trips API: expected 200, got {resp.status}"
        body = resp.json()
        assert body.get("result") is True, "trips API: result != true"
        expect(self.page.locator("table thead").first).to_be_visible(timeout=15000)
        self._assert_trip_headers()
        return resp

    def click_trip_filter_tab(self, tab: str):
        """Click a Trips status filter tab and validate API response."""
        with self.page.expect_response(
            lambda r: "/app/api/trip/" in r.url and r.request.method == "POST",
            timeout=30000,
        ) as resp_info:
            self.page.locator("div.flex-1.min-w-max, div.cursor-pointer").filter(
                has_text=re.compile(rf"^\s*{re.escape(tab)}\s*$")
            ).first.click()
        resp = resp_info.value
        assert resp.status == 200, f"trips [{tab}] API: expected 200, got {resp.status}"
        body = resp.json()
        assert body.get("result") is True, f"trips [{tab}] API: result != true"
        return resp

    def _assert_trip_headers(self):
        for header in TRIP_HEADERS:
            expect(
                self.page.locator(f"th:has-text('{header}')").first
            ).to_be_visible(timeout=5000)


# ── Print Waybills ─────────────────────────────────────────────────────────────

PRINT_WAYBILL_HEADERS = [
    "Darkstore", "User Name", "Printed At", "No. Of Labels", "File Size", "Action",
]


class PrintWaybillsPage:
    def __init__(self, page: Page):
        self.page = page

    def click_print_waybills_tab(self):
        """Click Print Waybills sidebar item → validates API + table headers."""
        with self.page.expect_response(
            lambda r: "/app/api/shipping-labels/" in r.url and r.request.method == "POST",
            timeout=30000,
        ) as resp_info:
            item = self.page.locator(".sidebar").get_by_text(
                re.compile(r"^\s*Print Waybills\s*$", re.IGNORECASE)
            ).last
            _ensure_pd_visible(self.page, item)
            item.click()
        resp = resp_info.value
        assert resp.status == 200, f"shipping-labels API: expected 200, got {resp.status}"
        body = resp.json()
        assert body.get("result") is True, "shipping-labels API: result != true"
        expect(self.page.locator("table thead").first).to_be_visible(timeout=15000)
        self._assert_headers()
        return resp

    def _assert_headers(self):
        for header in PRINT_WAYBILL_HEADERS:
            expect(
                self.page.locator(f"th:has-text('{header}')").first
            ).to_be_visible(timeout=5000)


# ── Express Hub ────────────────────────────────────────────────────────────────

EXPRESS_HUB_SHIPMENT_HEADERS = [
    "Shipment AWB", "Brand", "Slot", "SLA Status", "Shipment Status",
    "Breach", "Assignment", "Trip", "Action",
]

EXPRESS_HUB_RIDER_HEADERS = ["Rider Name", "Load", "Action"]


class ExpressHubPage:
    def __init__(self, page: Page):
        self.page = page

    def click_express_hub_tab(self):
        """Click Express Hub sidebar item → validates KPI API + both table headers."""
        with self.page.expect_response(
            lambda r: "/app/api/express-hub/kpi" in r.url and r.request.method == "GET",
            timeout=30000,
        ) as resp_info:
            item = self.page.locator(".sidebar").get_by_text(
                re.compile(r"^\s*Express Hub\s*$", re.IGNORECASE)
            ).last
            _ensure_pd_visible(self.page, item)
            item.click()
        resp = resp_info.value
        assert resp.status == 200, f"express-hub KPI API: expected 200, got {resp.status}"
        # Wait for both tables to render
        expect(self.page.locator("table").first).to_be_visible(timeout=15000)
        self._assert_shipment_headers()
        self._assert_rider_headers()
        return resp

    def _assert_shipment_headers(self):
        for header in EXPRESS_HUB_SHIPMENT_HEADERS:
            expect(
                self.page.locator(f"th:has-text('{header}')").first
            ).to_be_visible(timeout=5000)

    def _assert_rider_headers(self):
        for header in EXPRESS_HUB_RIDER_HEADERS:
            expect(
                self.page.locator(f"th:has-text('{header}')").first
            ).to_be_visible(timeout=5000)


# ── Store Transfer ─────────────────────────────────────────────────────────────

MANIFEST_HEADERS = [
    "Manifest No.", "Origin", "Destination", "Rider", "Status",
    "Total Shipments", "Vehicle Number", "Created At", "Updated At", "Action",
]

STORE_TRANSFER_SHIPMENT_HEADERS = [
    "Type", "Shipment ID", "Order ID", "Presence", "Origin",
    "Current Location", "Brand", "Manifest NO.", "Payment", "Value",
]


class StoreTransferPage:
    def __init__(self, page: Page):
        self.page = page

    def click_store_transfer_tab(self):
        """Click Store Transfer sidebar item → validates manifests API + manifest table headers."""
        with self.page.expect_response(
            lambda r: "/api/1/manifests/" in r.url
                      and r.request.method == "GET"
                      and "page" in r.url,
            timeout=30000,
        ) as resp_info:
            item = self.page.locator(".sidebar").get_by_text(
                re.compile(r"^\s*Store Transfer\s*$", re.IGNORECASE)
            ).last
            _ensure_pd_visible(self.page, item)
            item.click()
        resp = resp_info.value
        assert resp.status == 200, f"manifests API: expected 200, got {resp.status}"
        body = resp.json()
        assert "data" in body or "results" in body, "manifests API: unexpected response format"
        expect(self.page.locator("table thead").first).to_be_visible(timeout=15000)
        self._assert_manifest_headers()
        return resp

    def click_shipments_sub_tab(self):
        """Click Shipments sub-tab under Store Transfer → validates items API + headers."""
        with self.page.expect_response(
            lambda r: "/api/1/manifests/items/" in r.url and r.request.method == "GET",
            timeout=30000,
        ) as resp_info:
            self.page.get_by_role("button", name=re.compile(r"^\s*Shipments\s*$")).first.click()
        resp = resp_info.value
        assert resp.status == 200, f"manifests/items API: expected 200, got {resp.status}"
        body = resp.json()
        assert "data" in body or "results" in body, "manifests/items API: unexpected response format"
        expect(self.page.locator("table thead").first).to_be_visible(timeout=15000)
        self._assert_shipments_headers()
        return resp

    def _assert_manifest_headers(self):
        for header in MANIFEST_HEADERS:
            expect(
                self.page.locator(f"th:has-text('{header}')").first
            ).to_be_visible(timeout=5000)

    def _assert_shipments_headers(self):
        for header in STORE_TRANSFER_SHIPMENT_HEADERS:
            expect(
                self.page.locator(f"th:has-text('{header}')").first
            ).to_be_visible(timeout=5000)
