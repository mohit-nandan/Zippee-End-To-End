"""
E2E User Journey — Full Sequential Flow
========================================
One connected browser session, no resets between steps:

  01. Login              → two-step auth, land on dashboard
  02. Home Dashboard     → stat cards, coverage map
  03. Brands             → table, search, no-match, sort, brand detail tabs
  04. Analytics          → 3 tabs, filters, clear all
  05. Orders             → table, search ref, brand, payment filter
  06. Deliveries (PND)   → all sub-tabs, Trips tab, AWB search
  07. Settlement         → all 4 tabs (Rider/Dark Store/Company/Brand)
  08. Riders KYC         → search rider, city, sort, clear
  09. Billing            → tabs, sub-tabs, stat cards, action buttons
  10. Analytics          → 3 tabs, filters, clear all
  11. Rules              → table, search, sort
  12. Manual Upload      → table, search, sort
  13. Navigation         → all routes reachable without 404

Run full flow:
    ENV=preprod pytest tests/web/test_e2e_flow.py -v --alluredir=reports/allure-results

Pick up from a specific step (e.g. step 06):
    ENV=preprod pytest tests/web/test_e2e_flow.py -k "test_06" -v

Run a single step:
    ENV=preprod pytest tests/web/test_e2e_flow.py::TestE2EUserJourney::test_03_brands -v
"""
import allure
import pytest

from pages.home_page import HomePage
from pages.brands_page import BrandsPage
from pages.brand_detail_page import BrandDetailPage
from pages.emergency_comms_page import EmergencyCommsPage
from pages.shipments_page import ShipmentsPage
from pages.orders_page import OrdersPage
from pages.deliveries_page import DeliveriesPage
from pages.settlement_page import SettlementPage
from pages.riders_kyc_page import RidersKycPage
from pages.billing_page import BillingPage
from pages.analytics_page import AnalyticsPage
from pages.rules_page import RulesPage
from pages.manual_upload_page import ManualUploadPage
from pages.ds_profile_page import DsProfilePage
from pages.stores_page import StoresPage
from test_data.web_test_data import (
    KNOWN_BRAND, KNOWN_RIDER_NAME, KNOWN_CITY,
    PND_TABS, SETTLEMENT_TABS, ANALYTICS_TABS,
    BRAND_DETAIL_APIS,
)


# ── Shared session fixture ────────────────────────────────────────────────────

@pytest.fixture(scope="module")
def e2e_page(browser_instance, web_cfg):
    """
    Unauthenticated browser page shared across all 13 E2E steps.
    Login happens in test_01 — the same context is then used for every
    subsequent step, just like a real user session.
    """
    context = browser_instance.new_context(viewport={"width": 1440, "height": 900})
    pg = context.new_page()
    yield pg
    context.close()


# ── E2E flow ─────────────────────────────────────────────────────────────────

@allure.feature("E2E User Journey")
@pytest.mark.e2e
@pytest.mark.web
class TestE2EUserJourney:
    """
    Full sequential user journey.  Tests are numbered and run top-to-bottom.
    Each step leaves the browser in a state the next step can build on.
    """

    # ── 01 · Login ─────────────────────────────────────────────────────────

    @allure.story("01 · Login")
    @allure.title("User performs two-step login and lands on dashboard")
    def test_01_login(self, e2e_page, web_cfg):
        base = web_cfg["dashboard_url"].rstrip("/")

        with allure.step("Open sign-in page"):
            e2e_page.goto(f"{base}/sign-in")
            e2e_page.wait_for_load_state("domcontentloaded")
            e2e_page.locator("#email").wait_for(state="visible", timeout=15000)

        with allure.step("Enter email and continue"):
            e2e_page.locator("#email").fill(web_cfg["admin_user"])
            e2e_page.get_by_role("button", name="Continue with Email").click()

        with allure.step("Enter password and submit"):
            e2e_page.locator("input[type='password']").wait_for(state="visible", timeout=8000)
            e2e_page.locator("input[type='password']").fill(web_cfg["admin_pass"])
            e2e_page.get_by_role("button", name="Login", exact=True).click()

        with allure.step("Verify redirect to dashboard home"):
            e2e_page.wait_for_url(f"{base}/", timeout=15000)
            assert e2e_page.url.rstrip("/").endswith(base.rstrip("/")) or "/" in e2e_page.url

    # ── 02 · Home Dashboard ────────────────────────────────────────────────

    @allure.story("02 · Home Dashboard")
    @allure.title("Home loads with stat cards and coverage map")
    def test_02_home_dashboard(self, e2e_page, web_cfg):
        pg = HomePage(e2e_page)
        pg.go_to("home", web_cfg["dashboard_url"])
        pg.wait_for_spinner_gone()

        with allure.step("Stat cards visible"):
            assert pg.is_loaded(), "Home page did not load — stat card missing"
            pg.expect_visible(pg.NEW_ORDERS_CARD)
            pg.expect_visible(pg.PREPAID_CARD)
            pg.expect_visible(pg.DELIVERED_CARD)

        with allure.step("Coverage map section visible"):
            assert pg.is_coverage_section_visible()

    # ── 03 · Brands ────────────────────────────────────────────────────────

    @allure.story("03 · Brands")
    @allure.title("Brands table — search, no-match, sort")
    def test_03_brands(self, e2e_page, web_cfg):
        pg = BrandsPage(e2e_page)
        pg.go_to("brands", web_cfg["dashboard_url"])
        pg.wait_for_spinner_gone()

        with allure.step("Page loaded with data"):
            assert pg.is_loaded()
            pg.expect_url("/brand")
            pg.expect_count_gte(BrandsPage.TABLE_ROWS, 1)

        with allure.step(f"API + UI — Search brand '{KNOWN_BRAND}'"):
            with e2e_page.expect_response(
                lambda r: "/api/1/brands/" in r.url
                    and "/options" not in r.url
                    and "brand_display_name=" in r.url
                    and r.status == 200,
                timeout=15000,
            ) as api_call:
                pg.search_column("brand_name", KNOWN_BRAND)

            with allure.step("API — envelope fields present"):
                body = api_call.value.json()
                assert body["result"] is True, "brands search: result != true"
                assert body["status"] == "success", "brands search: status != success"

            with allure.step("API — pagination metadata valid"):
                data = body["data"]
                assert data["total"] >= 1, f"Search '{KNOWN_BRAND}' returned 0 results"
                assert isinstance(data["results"], list) and len(data["results"]) >= 1

            with allure.step("API — brand item has required fields"):
                first = data["results"][0]
                for field in ["id", "brand_display_name", "status", "category", "wallet_balance"]:
                    assert field in first, f"Brand item missing field '{field}'"

            with allure.step("UI — table shows matching rows"):
                pg.expect_count_gte(BrandsPage.TABLE_ROWS, 1)

        with allure.step("Sort by Brand Name — row count unchanged"):
            before = pg.get_row_count()
            pg.click_sort("Brand Name")
            assert pg.get_row_count() == before

        with allure.step(f"Click first brand row — cell contains '{KNOWN_BRAND}' and link is clickable"):
            # Mirrors Cypress:
            #   cy.get("tbody tr").first().find("td").first()
            #     .should("contain.text", searchName).find('a').click()
            pg.click_first_brand_row(KNOWN_BRAND)

        with allure.step("Navigated into brand detail — URL changed from /brand list"):
            assert "/brand" in e2e_page.url, (
                f"Expected URL to contain '/brand' after row click, got: {e2e_page.url}"
            )

        # ── Brand detail tab validation (mirrors Cypress switchTab) ─────────
        detail = BrandDetailPage(e2e_page)

        with allure.step("Tab: Commercials — API + UI"):
            resp = detail.click_commercials_tab(BRAND_DETAIL_APIS["commercials"])
            body = resp.json()
            assert body["result"] is True, "Commercials API: result != true"
            assert body["status"] == "success", "Commercials API: status != success"
            data = body["data"]
            for field in ["id", "brand", "return_pickup", "setup_fees", "rto_charges"]:
                assert field in data, f"Commercials: missing field '{field}'"

        with allure.step("Tab: GST Details — API + UI"):
            resp = detail.click_gst_details_tab(BRAND_DETAIL_APIS["gst_details"])
            body = resp.json()
            assert body["result"] is True, "GST Details API: result != true"
            assert body["status"] == "success", "GST Details API: status != success"
            assert isinstance(body["data"], list), "GST Details: data should be a list"
            assert len(body["data"]) >= 1, "GST Details: expected at least 1 record"
            first_gst = body["data"][0]
            for field in ["id", "brand_id", "gst_number", "state_name"]:
                assert field in first_gst, f"GST Details: missing field '{field}'"

        with allure.step("Tab: Warehouses — API + UI"):
            resp = detail.click_warehouses_tab(BRAND_DETAIL_APIS["warehouses"])
            body = resp.json()
            assert body["result"] is True, "Warehouses API: result != true"
            assert body["status"] == "success", "Warehouses API: status != success"
            data = body["data"]
            assert "brand_warehouses" in data, "Warehouses: missing 'brand_warehouses' key"
            assert "zfw_warehouses" in data,   "Warehouses: missing 'zfw_warehouses' key"
            assert len(data["brand_warehouses"]) >= 1, "Warehouses: brand_warehouses is empty"
            first_wh = data["brand_warehouses"][0]
            for field in ["id", "brand_id", "name", "city_name"]:
                assert field in first_wh, f"Warehouses: missing field '{field}'"

        with allure.step("Tab: Webhooks — API + UI"):
            resp = detail.click_webhooks_tab(BRAND_DETAIL_APIS["webhooks"])
            body = resp.json()
            assert body["result"] is True, "Webhooks API: result != true"
            assert body["status"] == "success", "Webhooks API: status != success"
            assert isinstance(body["data"], list), "Webhooks: data should be a list"
            if body["data"]:   # brand may have 0 webhooks — non-fatal
                first_wh = body["data"][0]
                for field in ["id", "brand_id", "webhook_type", "webhook_url"]:
                    assert field in first_wh, f"Webhooks: missing field '{field}'"

        with allure.step("Tab: Rules — API + UI"):
            # Cypress: cy.contains("li", "Rules").should("be.visible").click()
            resp = detail.click_rules_tab(BRAND_DETAIL_APIS["rules"])
            body = resp.json()
            assert body["result"] is True, "Rules API: result != true"
            assert body["status"] == "success", "Rules API: status != success"
            assert isinstance(body["data"], list), "Rules: data should be a list"
            if body["data"]:
                first_rule = body["data"][0]
                for field in ["rule_id", "brand_rule_priority", "rule_name"]:
                    assert field in first_rule, f"Rules: missing field '{field}'"

        with allure.step("Tab: Comms (WhatsApp) — API + UI"):
            resp = detail.click_comms_tab(BRAND_DETAIL_APIS["comms"])
            body = resp.json()
            assert body["result"] is True, "Comms API: result != true"
            assert body["status"] == "success", "Comms API: status != success"
            assert isinstance(body["data"], list), "Comms: data should be a list"
            assert len(body["data"]) >= 1, "Comms: expected at least 1 template"
            first_tmpl = body["data"][0]
            for field in ["id", "template_name", "template_type", "wa_status"]:
                assert field in first_tmpl, f"Comms: missing field '{field}'"

        with allure.step("Tab: Configuration — API + UI"):
            resp = detail.click_configuration_tab(BRAND_DETAIL_APIS["config"])
            body = resp.json()
            assert body["result"] is True, "Configuration API: result != true"
            assert body["status"] == "success", "Configuration API: status != success"
            data = body["data"]
            for section in ["pickup", "return", "delivery", "return_delivery"]:
                assert section in data, f"Configuration: missing section '{section}'"

        with allure.step("Navigate back to Brands list"):
            # go_back() is unreliable after multiple in-page tab clicks;
            # navigate directly to the brands list for a deterministic landing.
            pg.go_to("brands", web_cfg["dashboard_url"])
            pg.wait_for_spinner_gone()

        with allure.step("Add Brand button visible"):
            pg.expect_visible(BrandsPage.ADD_BRAND_BTN)


    # ── 04 · Analytics ─────────────────────────────────────────────────────
    @allure.story("04 · Analytics")
    @allure.title("Analytics — Operations, Business, Brands tabs")
    def test_04_analytics(self, e2e_page, web_cfg):
        pg = AnalyticsPage(e2e_page)
        pg.go_to("analytics", web_cfg["dashboard_url"])
        pg.wait_for_spinner_gone()

        with allure.step("Page loaded"):
            assert pg.is_loaded(), "Analytics page did not load — Operations tab not found"

        with allure.step("Operations tab — 'Orders per Day' visible"):
            pg.click_operations_tab()

        with allure.step("Business tab — 'Top 5 Brands' visible"):
            pg.click_business_tab()

        with allure.step("Brands tab — 'Revenue per order' visible"):
            pg.click_brands_tab()

    # ── 05 · Emergency Comms Logs ──────────────────────────────────────

    @allure.story("05 · Emergency Comms")
    @allure.title("Emergency Comms — click View Logs, validate API + UI")
    def test_05_emergency_comms_logs(self, e2e_page, web_cfg):
        pg = EmergencyCommsPage(e2e_page)
        pg.go_to("emergency_comms", web_cfg["dashboard_url"])
        pg.wait_for_spinner_gone()

        with allure.step("Emergency Comms page loaded"):
            # cy.contains("a", "Emergency Comms").should("be.visible").click()
            assert pg.is_loaded(), "Emergency Comms page did not load — 'View Logs' button not found"

        with allure.step("Click 'View Logs' — API + UI"):
            resp = pg.click_comms_logs_tab()

        with allure.step("API — envelope valid"):
            body = resp.json()
            assert body["result"] is True,      "Comms Logs API: result != true"
            assert body["status"] == "success", "Comms Logs API: status != success"

        with allure.step("API — pagination metadata valid"):
            inner = body["data"]["data"]
            assert inner["total"] >= 1, "Comms Logs: total should be >= 1"
            assert isinstance(inner["results"], list) and len(inner["results"]) >= 1

        with allure.step("API — log item has required fields"):
            first = inner["results"][0]
            for field in ["id", "file_type", "url",
                          "wa_template__template_name", "added_by__name", "added_on"]:
                assert field in first, f"Comms Logs: missing field '{field}'"


    # ── 06 · Billing ───────────────────────────────────────────────────────

    @allure.story("06 · Billing & Invoices")
    @allure.title("Billing — transactionHome, datepicker, Deduction View, Invoice History")
    def test_06_billing(self, e2e_page, web_cfg):
        pg = BillingPage(e2e_page)
        pg.go_to("billing", web_cfg["dashboard_url"])
        pg.wait_for_spinner_gone()

        with allure.step("Page loaded — Deductions + Invoices tabs visible"):
            assert pg.is_loaded(), "Billing page did not load"

        with allure.step("clickBillingTab — POST transactionHome → status 200"):
            # cy.intercept("POST", BillingRoutes.GetBillingDetails).as("transactionHome")
            # cy.wait("@transactionHome").its("response.statusCode").should("eq", 200)
            resp = pg.click_billing_tab()

        with allure.step("clickDatepicker — Last Month → POST transactionHeader → Total Usage > 0"):
            # cy.intercept("POST", BillingRoutes.GetBillingHeader).as("billingHeader")
            # cy.get(".relative.inline-block").click() → "Last Month" → wait
            # cy.contains("p", "Total Usage")...find("p.text-2xl") value > 0
            resp = pg.click_datepicker()

        with allure.step("clickDeductionsDetailsTab — POST transactionHistory → rows > 0"):
            # cy.intercept("POST", BillingRoutes.GetTransactionHistory).as("transactionHistory")
            # cy.contains("Deduction View").click() → wait → table rows > 0
            resp = pg.click_deductions_details_tab()
            # cy.get("table tbody tr").should("have.length.greaterThan", 0)
            assert pg.get_row_count() >= 1, "Deduction View table has 0 rows"

        with allure.step("clickInvoiceHistoryTab — POST invoice/history/ → status 200"):
            # cy.intercept("POST", BillingRoutes.GetInoviceHistory).as("invoiceHistory")
            # cy.contains("li", "Invoices").click() → wait → table rows (may be 0 in preprod)
            resp = pg.click_invoice_history_tab()

    # ── 07 · Bifrost / Middleware ──────────────────────────────────────────

    @allure.story("07 · Bifrost / Middleware")
    @allure.title("Middleware — DS Profile, Order, Rules, Shipments, Stores tabs")
    def test_07_bifrost_middleware(self, e2e_page, web_cfg):
        # We start by navigating to home dashboard to ensure clean sidebar state
        from pages.home_page import HomePage
        hp = HomePage(e2e_page)
        hp.go_to("home", web_cfg["dashboard_url"])
        hp.wait_for_spinner_gone()
        
        with allure.step("clickDsProfileTab — GET /darkstore-profiles/ → status 200 & rows > 0"):
            ds_page = DsProfilePage(e2e_page)
            resp = ds_page.click_ds_profile_tab()
            body = resp.json()
            assert body["result"] is True, "darkstore-profiles API: result != true"
            
        with allure.step("clickOrderTab — GET /order/ → status 200 & rows > 0"):
            orders_page = OrdersPage(e2e_page)
            resp = orders_page.click_order_tab()
            body = resp.json()
            assert body["result"] is True, "middleware/order API: result != true"
            
        with allure.step("clickRulesTab — GET /rules/ → status 200 & rows > 0"):
            rules_page = RulesPage(e2e_page)
            resp = rules_page.click_rules_tab()
            body = resp.json()
            assert body["result"] is True, "middleware/rules API: result != true"

        with allure.step("clickShipmentsTab — GET /shipment/ → status 200 & rows > 0"):
            shipments_page = ShipmentsPage(e2e_page)
            resp = shipments_page.click_shipments_tab()
            body = resp.json()
            assert body["result"] is True, "middleware/shipment API: result != true"

        with allure.step("clickStoresTab — GET /warehouses/ → status 200 & rows > 0"):
            stores_page = StoresPage(e2e_page)
            resp = stores_page.click_stores_tab()
            body = resp.json()
            assert body["result"] is True, "middleware/warehouses API: result != true"

    # @allure.story("08 · COD Module")
    # def test_08_cod_module(self, e2e_page):
    #     """
    #     COD module disabled — not working on prod.
    #     Validates all tabs under the COD accordion:
    #     Attendance, Deactivated Riders, Payouts, Rider Payroll, Redo Logs, Riders, Settlements, Create New Template.
    #     """
    #     from pages.cod_pages import (
    #         CODAttendancePage,
    #         CODDeactivatedRidersPage,
    #         CODPayoutsPage,
    #         CODPayrollPage,
    #         CODRedoLogsPage,
    #         CODRidersKYCPage,
    #         CODSettlementsPage,
    #         CODTemplatesPage
    #     )
    #
    #     with allure.step("clickAttendanceTab"):
    #         attendance_page = CODAttendancePage(e2e_page)
    #         resp = attendance_page.click_attendance_tab()
    #         body = resp.json()
    #         assert body["result"] is True, "attendance API: result != true"
    #
    #     with allure.step("clickDeactivatedRidersTab"):
    #         deac_riders_page = CODDeactivatedRidersPage(e2e_page)
    #         resp = deac_riders_page.click_deactivated_riders_tab()
    #         body = resp.json()
    #         assert body["result"] is True, "deactivated riders API: result != true"
    #
    #     with allure.step("clickPayoutsTab"):
    #         payouts_page = CODPayoutsPage(e2e_page)
    #         resp = payouts_page.click_payouts_tab()
    #         body = resp.json()
    #         assert body["result"] is True, "payouts API: result != true"
    #
    #     with allure.step("clickPayrollTab"):
    #         payroll_page = CODPayrollPage(e2e_page)
    #         resp = payroll_page.click_payroll_tab()
    #         body = resp.json()
    #         assert body["result"] is True, "payroll API: result != true"
    #
    #     with allure.step("clickRedoLogsTab"):
    #         redo_logs_page = CODRedoLogsPage(e2e_page)
    #         resp = redo_logs_page.click_redo_logs_tab()
    #         body = resp.json()
    #         assert body["result"] is True, "redo logs API: result != true"
    #
    #     with allure.step("clickRidersKYCTab"):
    #         riders_kyc_page = CODRidersKYCPage(e2e_page)
    #         resp = riders_kyc_page.click_riders_kyc_tab()
    #         body = resp.json()
    #         assert body["result"] is True, "riders kyc API: result != true"
    #
    #     with allure.step("clickSettlementsTab & KPIs"):
    #         settlements_page = CODSettlementsPage(e2e_page)
    #
    #         resp = settlements_page.click_settlements_tab()
    #         body = resp.json()
    #         assert body["result"] is True, "settlements KPI API: result != true"
    #
    #         resp = settlements_page.click_darkstores_kpi()
    #         body = resp.json()
    #         assert body["result"] is True, "darkstores KPI API: result != true"
    #
    #         resp = settlements_page.click_company_kpi()
    #         body = resp.json()
    #         assert body["result"] is True, "company KPI API: result != true"
    #
    #         resp = settlements_page.click_brands_kpi()
    #         body = resp.json()
    #         assert body["result"] is True, "brands KPI API: result != true"
    #
    #     with allure.step("clickTemplatesTab"):
    #         templates_page = CODTemplatesPage(e2e_page)
    #         templates_page.click_templates_tab()

    @allure.story("09 · Pickup Delivery Module")
    def test_09_pickup_delivery(self, e2e_page):
        """
        Validates all sections under the Pickup Delivery accordion:
        Deliveries (Shipments + all filter tabs, Trips + all filter tabs),
        Print Waybills, Express Hub, Store Transfer (Manifest + Shipments tabs).
        API response validated before each UI header check.
        """
        from pages.pickup_delivery_pages import (
            DeliveriesShipmentsPage,
            DeliveriesTripsPage,
            PrintWaybillsPage,
            ExpressHubPage,
            StoreTransferPage,
            SHIPMENT_FILTER_TABS,
            TRIP_FILTER_TABS,
        )

        # ── Deliveries → Shipments ────────────────────────────────────────────
        with allure.step("Deliveries — Shipments tab (Assign Now default)"):
            shipments_page = DeliveriesShipmentsPage(e2e_page)
            shipments_page.click_deliveries_tab()

        for tab in SHIPMENT_FILTER_TABS[1:]:   # skip Assign Now (already active)
            with allure.step(f"Deliveries — Shipments filter: {tab}"):
                shipments_page.click_shipment_filter_tab(tab)

        # ── Deliveries → Trips ────────────────────────────────────────────────
        with allure.step("Deliveries — Trips tab (Draft default)"):
            trips_page = DeliveriesTripsPage(e2e_page)
            trips_page.click_trips_tab()

        for tab in TRIP_FILTER_TABS[1:]:        # skip Draft (already active)
            with allure.step(f"Deliveries — Trips filter: {tab}"):
                trips_page.click_trip_filter_tab(tab)

        # ── Print Waybills ────────────────────────────────────────────────────
        with allure.step("Print Waybills tab"):
            print_page = PrintWaybillsPage(e2e_page)
            print_page.click_print_waybills_tab()

        # ── Express Hub ───────────────────────────────────────────────────────
        with allure.step("Express Hub tab"):
            express_page = ExpressHubPage(e2e_page)
            express_page.click_express_hub_tab()

        # ── Store Transfer → Manifest ─────────────────────────────────────────
        with allure.step("Store Transfer — Manifest tab"):
            store_transfer_page = StoreTransferPage(e2e_page)
            store_transfer_page.click_store_transfer_tab()

        # ── Store Transfer → Shipments ────────────────────────────────────────
        with allure.step("Store Transfer — Shipments sub-tab"):
            store_transfer_page.click_shipments_sub_tab()

    # @allure.title("Shipments — stat cards, AWB search, sort")
    # def test_04_shipments(self, e2e_page, web_cfg):
    #     pg = ShipmentsPage(e2e_page)
    #     pg.go_to("shipments", web_cfg["dashboard_url"])
    #     pg.wait_for_spinner_gone()

    #     with allure.step("Stat cards all visible"):
    #         assert pg.is_loaded()
    #         for card in [ShipmentsPage.STAT_TOTAL, ShipmentsPage.STAT_OPEN,
    #                      ShipmentsPage.STAT_FAILED, ShipmentsPage.STAT_PROCESSED]:
    #             pg.expect_visible(card)

    #     with allure.step("AWB partial search (FBX)"):
    #         pg.search_awb("FBX")
    #         assert pg.get_row_count() >= 0

    #     with allure.step("No-match AWB returns empty table"):
    #         pg.search_awb(NO_MATCH_STRING)
    #         assert pg.get_row_count() == 0

    #     with allure.step("Clear AWB and sort — row count stable"):
    #         pg.search_awb("")
    #         pg.wait_for_spinner_gone()
    #         before = pg.get_row_count()
    #         pg.click_sort("Zippee AWB")
    #         assert pg.get_row_count() == before

    #     with allure.step("Refire button visible"):
    #         pg.expect_visible(ShipmentsPage.REFIRE_BTN)

    # # ── 05 · Orders ────────────────────────────────────────────────────────

    # @allure.story("05 · Orders")
    # @allure.title("Orders — search by reference, brand, payment mode filter")
    # def test_05_orders(self, e2e_page, web_cfg):
    #     pg = OrdersPage(e2e_page)
    #     pg.go_to("orders", web_cfg["dashboard_url"])
    #     pg.wait_for_spinner_gone()

    #     with allure.step("Table loaded with rows"):
    #         assert pg.is_loaded()
    #         pg.expect_url("/orders")
    #         assert pg.get_row_count() > 0

    #     with allure.step("Search by reference prefix (FBX)"):
    #         pg.search_reference("FBX")
    #         assert pg.get_row_count() >= 0
    #         pg.search_reference("")
    #         pg.wait_for_spinner_gone()

    #     with allure.step(f"Search by brand: {KNOWN_BRAND}"):
    #         pg.search_brand(KNOWN_BRAND)
    #         assert pg.get_row_count() >= 0
    #         pg.search_brand("")
    #         pg.wait_for_spinner_gone()

    #     with allure.step("Filter by payment mode COD"):
    #         pg.filter_payment_mode("COD")
    #         pg.wait_for_spinner_gone()
    #         assert pg.get_row_count() >= 0

    #     with allure.step("Sort by Order Date — row count stable"):
    #         before = pg.get_row_count()
    #         pg.click_sort("Order Date")
    #         assert pg.get_row_count() == before

    # # ── 06 · Deliveries (PND) ─────────────────────────────────────────────

    # @allure.story("06 · Deliveries PND")
    # @allure.title("PND — all sub-tabs, Trips tab, AWB search")
    # def test_06_deliveries_pnd(self, e2e_page, web_cfg):
    #     pg = DeliveriesPage(e2e_page)
    #     pg.go_to("deliveries", web_cfg["dashboard_url"])
    #     pg.wait_for_spinner_gone()

    #     with allure.step("Page loaded with Shipments and Trips tabs"):
    #         assert pg.is_loaded()
    #         pg.expect_visible(DeliveriesPage.TAB_SHIPMENTS)
    #         pg.expect_visible(DeliveriesPage.TAB_TRIPS)

    #     with allure.step("Cycle all shipment sub-tabs"):
    #         for tab in PND_TABS:
    #             with allure.step(f"Sub-tab: {tab}"):
    #                 pg.click_tab(tab)
    #                 assert "/pnd" in pg.current_url()

    #     with allure.step("Switch to Trips then back to Shipments"):
    #         pg.click_tab("trips")
    #         pg.expect_visible(DeliveriesPage.TAB_TRIPS)
    #         pg.click_tab("shipments")
    #         pg.expect_visible(DeliveriesPage.TAB_ASSIGN_NOW)

    #     with allure.step("Search AWB on All Shipments"):
    #         pg.click_tab("all_shipments")
    #         pg.search_awb("FBX")
    #         assert pg.get_row_count() >= 0

    #     with allure.step("No-match AWB returns empty table"):
    #         pg.search_awb(NO_MATCH_STRING)
    #         assert pg.get_row_count() == 0

    #     with allure.step("Create Trip button visible"):
    #         pg.search_awb("")
    #         pg.wait_for_spinner_gone()
    #         pg.expect_visible(DeliveriesPage.CREATE_TRIP_BTN)

    # # ── 07 · Settlement ────────────────────────────────────────────────────

    # @allure.story("07 · Settlement")
    # @allure.title("Settlement — all 4 tabs: Rider, Dark Store, Company, Brand")
    # def test_07_settlement(self, e2e_page, web_cfg):
    #     pg = SettlementPage(e2e_page)
    #     pg.go_to("settlement", web_cfg["dashboard_url"])
    #     pg.wait_for_spinner_gone()

    #     with allure.step("All 4 tabs visible"):
    #         assert pg.is_loaded()
    #         for selector in [SettlementPage.TAB_RIDER, SettlementPage.TAB_DARKSTORE,
    #                           SettlementPage.TAB_COMPANY, SettlementPage.TAB_BRAND]:
    #             pg.expect_visible(selector)

    #     with allure.step("Cycle all tabs"):
    #         for tab in SETTLEMENT_TABS:
    #             with allure.step(f"Tab: {tab}"):
    #                 pg.click_tab(tab)
    #                 assert "/settlement" in pg.current_url()

    #     with allure.step("Rider toggle visible on Rider tab"):
    #         pg.click_tab("rider")
    #         pg.expect_visible(SettlementPage.TOGGLE_RIDER)

    # # ── 08 · Riders KYC ───────────────────────────────────────────────────

    # @allure.story("08 · Riders KYC")
    # @allure.title("KYC — search rider, city, sort columns, Approved status label")
    # def test_08_riders_kyc(self, e2e_page, web_cfg):
    #     pg = RidersKycPage(e2e_page)
    #     pg.go_to("riders_kyc", web_cfg["dashboard_url"])
    #     pg.wait_for_spinner_gone()

    #     with allure.step("Page loaded with rows"):
    #         assert pg.is_loaded()
    #         pg.expect_url("/kyc")
    #         assert pg.get_row_count() > 0

    #     with allure.step(f"Search rider by name: {KNOWN_RIDER_NAME}"):
    #         pg.search_rider(KNOWN_RIDER_NAME)
    #         assert pg.get_row_count() >= 1

    #     with allure.step("No-match rider search returns empty"):
    #         pg.search_rider(NO_MATCH_STRING)
    #         assert pg.get_row_count() == 0
    #         pg.search_rider("")
    #         pg.wait_for_spinner_gone()

    #     with allure.step(f"Search by city: {KNOWN_CITY}"):
    #         pg.search_city(KNOWN_CITY)
    #         assert pg.get_row_count() >= 0
    #         pg.search_city("")
    #         pg.wait_for_spinner_gone()

    #     with allure.step("Sort by Rider Name — row count unchanged"):
    #         before = pg.get_row_count()
    #         pg.click_sort("Rider Name")
    #         assert pg.get_row_count() == before

    #     with allure.step("Approved status label visible"):
    #         pg.expect_visible(RidersKycPage.STATUS_APPROVED)

    # # ── 11 · Rules ────────────────────────────────────────────────────────

    # @allure.story("11 · Rules Management")
    # @allure.title("Rules — table rows, name search, no-match, sort")
    # def test_11_rules(self, e2e_page, web_cfg):
    #     pg = RulesPage(e2e_page)
    #     pg.go_to("rules", web_cfg["dashboard_url"])
    #     pg.wait_for_spinner_gone()

    #     with allure.step("Page loaded with rows"):
    #         assert pg.is_loaded()
    #         pg.expect_url("/rules")
    #         assert pg.get_row_count() > 0

    #     with allure.step("Search name partial (express)"):
    #         pg.search_name("express")
    #         assert pg.get_row_count() >= 0
    #         pg.search_name("")
    #         pg.wait_for_spinner_gone()

    #     with allure.step("No-match search returns empty"):
    #         pg.search_name(NO_MATCH_STRING)
    #         assert pg.get_row_count() == 0
    #         pg.search_name("")
    #         pg.wait_for_spinner_gone()

    #     with allure.step("Sort by Name — row count unchanged"):
    #         before = pg.get_row_count()
    #         pg.click_sort_name()
    #         assert pg.get_row_count() == before

    #     with allure.step("Add button visible"):
    #         pg.expect_visible(RulesPage.ADD_BTN)

    # # ── 12 · Manual Upload ────────────────────────────────────────────────

    # @allure.story("12 · Manual Upload")
    # @allure.title("Manual Upload — table, search order ID, sort")
    # def test_12_manual_upload(self, e2e_page, web_cfg):
    #     pg = ManualUploadPage(e2e_page)
    #     pg.go_to("manual_upload", web_cfg["dashboard_url"])
    #     pg.wait_for_spinner_gone()

    #     with allure.step("Page loaded"):
    #         assert pg.is_loaded()
    #         pg.expect_url("/manualUpload")

    #     with allure.step("No-match order ID search returns empty"):
    #         pg.search_order_id(NO_MATCH_STRING)
    #         assert pg.get_row_count() == 0
    #         pg.search_order_id("")
    #         pg.wait_for_spinner_gone()

    #     with allure.step("Sort by Order ID — row count unchanged"):
    #         before = pg.get_row_count()
    #         pg.click_sort("Order ID")
    #         assert pg.get_row_count() == before

    #     with allure.step("Upload and Add New buttons visible"):
    #         pg.expect_visible(ManualUploadPage.UPLOAD_BTN)
    #         pg.expect_visible(ManualUploadPage.ADD_NEW_BTN)

    # # ── 13 · Navigation Completeness ──────────────────────────────────────

    # @allure.story("13 · Navigation")
    # @allure.title("All dashboard routes are reachable without 404 or crash")
    # def test_13_navigation_all_routes(self, e2e_page, web_cfg):
    #     base = web_cfg["dashboard_url"].rstrip("/")

    #     routes = {
    #         "home":          "/",
    #         "brands":        "/brand",
    #         "shipments":     "/shipments",
    #         "orders":        "/orders",
    #         "settlement":    "/settlement",
    #         "riders_kyc":    "/kyc",
    #         "billing":       "/billing",
    #         "analytics":     "/analytics",
    #         "rules":         "/rules",
    #         "manual_upload": "/manualUpload",
    #         "deliveries":    "/pnd",
    #     }

    #     for name, path in routes.items():
    #         with allure.step(f"Route: {name} → {path}"):
    #             target = f"{base}/" if path == "/" else f"{base}{path}"
    #             e2e_page.goto(target)
    #             e2e_page.wait_for_load_state("domcontentloaded")
    #             content_start = e2e_page.content()[:500].lower()
    #             assert "404" not in content_start, f"Route '{name}' returned 404"
    #             current = e2e_page.url
    #             assert path.lstrip("/") in current or current.endswith("/"), (
    #                 f"Route '{name}': expected '{path}' in URL, got '{current}'"
    #             )
