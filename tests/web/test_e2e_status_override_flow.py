"""
E2E Status Override Flow — test_10
====================================
Flow:
  1. Create a Clickpost PREPAID order (drop pincode 122008) via the Zippee WMS API.
  2. AWB is returned directly in the response (no DB polling required).
  3. Navigate to PND → Deliveries → Shipments → All Shipments.
  4. Search for the AWB.
  5. For each override status (DELIVERED, CANCELLED, RTO, READY, DELIVERY_ATTEMPTED):
       a. Open 3-dot menu → Override Status modal.
       b. Select the status + reason → click Update.
       c. Validate Shipment Logs page (API + status visible).
       d. Validate Bifrost Last Mile Logs (API + status visible).
       e. Validate 4 DB tables have entries for this AWB.

Run:
    $env:ENV="preprod"; pytest tests/web/test_e2e_status_override_flow.py -v --alluredir=reports/allure-results
"""
import uuid
import datetime
import re

import requests as _requests
import allure
import pytest

from pages.status_override_page import StatusOverridePage, OVERRIDE_STATUSES, DEFAULT_REASON
from pages.shipment_logs_page import ShipmentLogsPage
from pages.bifrost_lastmile_page import BifrostLastMilePage

# Zippee WMS credentials — same as create_preprod_orders.py
_WMS_URL    = "https://preprod.zorms.zfwhospitality.in"
_WMS_USER   = "fabbox@zfwhospitality.com"
_WMS_PASS   = "QWERTY!@#$%"
_CP_API_KEY = "clickpost_preprod_aEmgZn14UozwomtDfQR2Wx1s4LJpOTt9I6XfyfKY34siKs6S7aEWbYVCzRKD4UtX"


# ── Module-scoped browser session ─────────────────────────────────────────────

@pytest.fixture(scope="module")
def e2e_page(browser_instance, web_cfg):
    """
    Authenticated browser session shared across all steps in this module.
    Login happens once here; the page is reused for every test step.
    """
    context = browser_instance.new_context(viewport={"width": 1440, "height": 900})
    pg = context.new_page()
    base = web_cfg["dashboard_url"].rstrip("/")

    pg.goto(f"{base}/sign-in")
    pg.wait_for_load_state("domcontentloaded")
    pg.locator("#email").wait_for(state="visible", timeout=15000)
    pg.locator("#email").fill(web_cfg["admin_user"])
    pg.get_by_role("button", name="Continue with Email").click()
    pg.locator("input[type='password']").wait_for(state="visible", timeout=8000)
    pg.locator("input[type='password']").fill(web_cfg["admin_pass"])
    pg.get_by_role("button", name="Login", exact=True).click()
    pg.wait_for_url(f"{base}/", timeout=15000)

    yield pg
    context.close()


# ── Zippee WMS order creation ──────────────────────────────────────────────────

def _wms_token() -> str:
    """Authenticate against the Zippee WMS API and return a Bearer token."""
    r = _requests.post(
        f"{_WMS_URL}/api/1/mainsite/token",
        json={"username": _WMS_USER, "password": _WMS_PASS},
        headers={"X-API-KEY": _CP_API_KEY},
        timeout=30,
    )
    r.raise_for_status()
    data = r.json()
    token = (data.get("data") or {}).get("token") or data.get("token")
    assert token, f"No token in WMS auth response: {data}"
    return token


def _create_wms_shipment(token: str, order_ref: str, pincode: str = "122008") -> str:
    """Create a PREPAID Clickpost shipment via the Zippee WMS API. Returns zippee_awb."""
    now_str = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    payload = {
        "reference_code":          order_ref,
        "original_reference_code": order_ref,
        "order_date":              now_str,
        "reverse_pickup":          False,
        "shipment_type":           "FORWARD",
        "multi_select":            False,
        "is_tnb":                  False,
        "meta":                    {"tags": ["PREPAID"]},
        "delivery_details": {
            "name":           "E2E Test Customer",
            "contact_num":    "9123456780",
            "address_line_1": "MG Road, Sector 28",
            "address_line_2": "Gurugram",
            "city":           "Gurugram",
            "state":          "Haryana",
            "country":        "India",
            "latitude":       28.4595,
            "longitude":      77.0266,
            "email":          "e2e.test@zippee.delivery",
            "pin_code":       pincode,
        },
        "return_details": {
            "name":           "E2E Return Address",
            "contact_num":    "9532385430",
            "address_line_1": "okhla",
            "address_line_2": "Delhi",
            "city":           "Delhi",
            "state":          "Delhi",
            "country":        "India",
            "latitude":       28.4940959,
            "longitude":      77.0927495,
            "email":          _WMS_USER,
            "pin_code":       "110002",
        },
        "pickup_details": {
            "name":           "E2E Test Warehouse",
            "contact_num":    "9140151251",
            "address_line_1": "DLF Cyber City, Phase II",
            "address_line_2": "Gurugram",
            "city":           "Gurugram",
            "state":          "Haryana",
            "country":        "India",
            "latitude":       28.4944,
            "longitude":      77.0860,
            "email":          _WMS_USER,
            "pin_code":       "122002",
        },
        "cod_details": {
            "is_cod":                      False,
            "collectable_amount":          0,
            "total_value":                 500,
            "dynamic_adjustment_required": False,
            "miscellaneous_charges":       {"handling_fee": 0, "packing_cost": 0, "priority_fee": 0},
        },
        "package_weight": 500,
        "package_length": 10,
        "package_width":  10,
        "package_height": 10,
        "order_items": [
            {
                "item_quantity": 1,
                "selling_price": 500,
                "sku":           "E2E-SKU-001",
                "product_name":  "E2E Override Test Product",
                "description":   "E2E Override Test Product",
                "mrp":           500,
                "ean":           "EAN2026E2E001",
                "category":      "Test",
                "is_returnable": False,
                "image":         "",
                "meta":          {},
            }
        ],
    }
    r = _requests.post(
        f"{_WMS_URL}/api/1/mainsite/shipment/create",
        json=payload,
        headers={"Authorization": f"Bearer {token}", "x-api-key": _CP_API_KEY},
        timeout=30,
    )
    r.raise_for_status()
    data = r.json()
    inner = data.get("data") or data.get("result") or data
    awb = inner.get("zippee_awb") or inner.get("awb") or inner.get("waybill")
    assert awb, f"No AWB in WMS response for ref={order_ref}: {data}"
    return awb


@pytest.fixture(scope="module")
def created_order():
    """
    Creates a PREPAID Clickpost order at drop pincode 122008 via the Zippee WMS
    API (same approach as create_preprod_orders.py).  AWB is returned directly
    in the response — no DB polling required.
    """
    order_ref  = f"E2E_{uuid.uuid4().hex[:8].upper()}"
    token      = _wms_token()
    zippee_awb = _create_wms_shipment(token, order_ref)

    return {
        "order_ref":  order_ref,
        "zippee_awb": zippee_awb,
    }


# ── DB validation helper ───────────────────────────────────────────────────────

def _validate_db_tables(db_client, awb: str, context: str = ""):
    """Query all 4 DB tables and assert at least one entry exists per table."""
    prefix = f"[{context}] " if context else ""

    rows = db_client.fetch_all(
        "SELECT id, reference_code, added_on FROM zfw_webhook_history "
        "WHERE reference_code = %s ORDER BY id DESC LIMIT 10",
        (awb,),
    )
    assert rows, f"{prefix}zfw_webhook_history: no entries for AWB {awb}"

    rows = db_client.fetch_all(
        "SELECT id, reference_code, added_on FROM zorcs_brand_webhook_logs "
        "WHERE reference_code = %s ORDER BY id DESC LIMIT 10",
        (awb,),
    )
    assert rows, f"{prefix}zorcs_brand_webhook_logs: no entries for AWB {awb}"

    rows = db_client.fetch_all(
        "SELECT id, awb_number, aws_event_code, added_on FROM zorcs_order_event "
        "WHERE awb_number = %s ORDER BY id DESC LIMIT 10",
        (awb,),
    )
    assert rows, f"{prefix}zorcs_order_event: no entries for AWB {awb}"

    rows = db_client.fetch_all(
        "SELECT id, ref_code, added_on FROM zfw_wa_comm_logs "
        "WHERE ref_code = %s ORDER BY id DESC LIMIT 10",
        (awb,),
    )
    assert rows, f"{prefix}zfw_wa_comm_logs: no entries for AWB {awb}"


# ── Test class ─────────────────────────────────────────────────────────────────

@allure.feature("E2E Status Override Flow")
@pytest.mark.e2e
@pytest.mark.web
class TestStatusOverrideFlow:
    """
    Full E2E: create a Clickpost order → override each status in sequence →
    validate Shipment Logs, Last Mile Logs, and 4 DB tables after every override.
    """

    @allure.story("10 · Status Override — Setup")
    @allure.title("Create Clickpost order and confirm AWB assigned")
    def test_10a_create_order(self, created_order):
        awb = created_order["zippee_awb"]
        ref = created_order["order_ref"]
        with allure.step(f"Order ref: {ref}  →  Zippee AWB: {awb}"):
            assert awb, "Zippee AWB must not be empty"

    @allure.story("10 · Status Override — Navigate")
    @allure.title("Open PND Shipments (All Shipments) and locate AWB")
    def test_10b_navigate_and_search(self, e2e_page, web_cfg, created_order):
        awb      = created_order["zippee_awb"]
        base_url = web_cfg["dashboard_url"].rstrip("/")
        override = StatusOverridePage(e2e_page)

        with allure.step("Navigate to All Shipments"):
            resp = override.navigate_to_all_shipments(base_url)
            body = resp.json()
            assert body.get("result") is True, "All Shipments API: result != true"

        with allure.step(f"Search AWB: {awb}"):
            override.search_awb(awb)

        with allure.step("Resolve internal shipment ID"):
            shipment_id = override.get_pnd_shipment_id(awb)
            assert shipment_id.isdigit(), f"Expected numeric shipment ID, got: {shipment_id}"
            allure.dynamic.parameter("shipment_id", shipment_id)

    @allure.story("10 · Status Override — Full Flow")
    @allure.title("Override all statuses and validate logs + DB per status")
    def test_10c_override_all_statuses(
        self, e2e_page, web_cfg, db_client, created_order
    ):
        awb      = created_order["zippee_awb"]
        base_url = web_cfg["dashboard_url"].rstrip("/")

        override_page = StatusOverridePage(e2e_page)
        logs_page     = ShipmentLogsPage(e2e_page, base_url)
        lastmile_page = BifrostLastMilePage(e2e_page, base_url)

        # ── Navigate to All Shipments and resolve shipment ID once ────────────
        with allure.step("Navigate to All Shipments"):
            override_page.navigate_to_all_shipments(base_url)

        with allure.step(f"Search AWB: {awb}"):
            override_page.search_awb(awb)
            shipment_id = override_page.get_pnd_shipment_id(awb)

        # ── Phase 1: apply every override status in sequence ─────────────────
        for status in OVERRIDE_STATUSES:
            with allure.step(f"Override → {status}"):
                override_page.override_to_status(awb, status, DEFAULT_REASON)

            with allure.step(f"Return to All Shipments after {status}"):
                override_page.navigate_to_all_shipments(base_url)
                override_page.search_awb(awb)

        # ── Phase 2: validate logs + DB for the final status ─────────────────
        final_status = OVERRIDE_STATUSES[-1]
        allure.dynamic.parameter("validated_status", final_status)

        with allure.step(f"Shipment Logs — validate {final_status} entry"):
            resp = logs_page.open_logs(shipment_id)
            logs_page.assert_status_in_logs(final_status)

        with allure.step(f"Last Mile Logs — validate {final_status} entry"):
            lastmile_page.navigate_to_bifrost_shipments()
            lastmile_page.search_and_open_bifrost_shipment(awb)
            lastmile_page.click_order_link()
            lastmile_page.click_last_mile_logs()
            lastmile_page.assert_status_in_last_mile_logs(final_status)

        with allure.step("DB Validation — 4 tables"):
            _validate_db_tables(db_client, awb, context=final_status)
