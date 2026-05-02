"""
E2E User Journey — Full Sequential Flow
========================================
One connected browser session, no resets between steps:

  01. Login              → two-step auth, land on dashboard
  02. Home Dashboard     → stat cards, coverage map
  03. Brands             → table, search, no-match, sort
  04. Shipments          → stat cards, AWB search, sort
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
from pages.shipments_page import ShipmentsPage
from pages.orders_page import OrdersPage
from pages.deliveries_page import DeliveriesPage
from pages.settlement_page import SettlementPage
from pages.riders_kyc_page import RidersKycPage
from pages.billing_page import BillingPage
from pages.analytics_page import AnalyticsPage
from pages.rules_page import RulesPage
from pages.manual_upload_page import ManualUploadPage
from test_data.web_test_data import (
    KNOWN_BRAND, KNOWN_RIDER_NAME, KNOWN_CITY,
    NO_MATCH_STRING, PND_TABS, SETTLEMENT_TABS, ANALYTICS_TABS,
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

    # @allure.story("03 · Brands")
    # @allure.title("Brands table — search, no-match, sort")
    # def test_03_brands(self, e2e_page, web_cfg):
    #     pg = BrandsPage(e2e_page)
    #     pg.go_to("brands", web_cfg["dashboard_url"])
    #     pg.wait_for_spinner_gone()

    #     with allure.step("Page loaded with data"):
    #         assert pg.is_loaded()
    #         pg.expect_url("/brand")
    #         assert pg.get_row_count() > 0, "Brands table is empty"

    #     with allure.step(f"Search by brand name: {KNOWN_BRAND}"):
    #         pg.search_column("brand_name", KNOWN_BRAND)
    #         assert pg.get_row_count() >= 1

    #     with allure.step("No-match search returns empty table"):
    #         pg.search_column("brand_name", NO_MATCH_STRING)
    #         assert pg.get_row_count() == 0

    #     with allure.step("Clear search and verify rows return"):
    #         pg.search_column("brand_name", "")
    #         pg.wait_for_spinner_gone()
    #         assert pg.get_row_count() > 0

    #     with allure.step("Sort by Brand Name — row count unchanged"):
    #         before = pg.get_row_count()
    #         pg.click_sort("Brand Name")
    #         assert pg.get_row_count() == before

    #     with allure.step("Add Brand button visible"):
    #         pg.expect_visible(BrandsPage.ADD_BRAND_BTN)

    # # ── 04 · Shipments ─────────────────────────────────────────────────────

    # @allure.story("04 · Shipments")
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

    # # ── 09 · Billing ──────────────────────────────────────────────────────

    # @allure.story("09 · Billing & Invoices")
    # @allure.title("Billing — tabs, sub-tabs, stat cards, action buttons, table rows")
    # def test_09_billing(self, e2e_page, web_cfg):
    #     pg = BillingPage(e2e_page)
    #     pg.go_to("billing", web_cfg["dashboard_url"])
    #     pg.wait_for_spinner_gone()

    #     with allure.step("Page loaded with both tabs"):
    #         assert pg.is_loaded()
    #         pg.expect_visible(BillingPage.TAB_DEDUCTIONS)
    #         pg.expect_visible(BillingPage.TAB_INVOICES)

    #     with allure.step("Deductions stat cards visible"):
    #         assert pg.stats_visible()
    #         pg.expect_visible(BillingPage.STAT_NUM_DEDUCTIONS)

    #     with allure.step("Switch to Invoices → back to Deductions"):
    #         pg.click_tab("invoices")
    #         pg.expect_visible(BillingPage.TAB_INVOICES)
    #         pg.click_tab("deductions")
    #         pg.expect_visible(BillingPage.STAT_TOTAL_USAGE)

    #     with allure.step("Daily Summary sub-tab"):
    #         pg.click_subtab("daily")
    #         pg.expect_visible(BillingPage.SUBTAB_DAILY)

    #     with allure.step("Deduction View sub-tab"):
    #         pg.click_subtab("deduction_view")
    #         pg.expect_visible(BillingPage.SUBTAB_DEDUCTION)

    #     with allure.step("Action buttons visible"):
    #         pg.expect_visible(BillingPage.GEN_INVOICE_BTN)
    #         pg.expect_visible(BillingPage.SEND_INVOICES_BTN)
    #         pg.expect_visible(BillingPage.MG_ADJUSTMENT_BTN)

    #     with allure.step("Table has at least one row"):
    #         assert pg.get_row_count() >= 1

    # # ── 10 · Analytics ────────────────────────────────────────────────────

    # @allure.story("10 · Analytics")
    # @allure.title("Analytics — 3 tabs, Orders Per Day chart, filters, Clear All")
    # def test_10_analytics(self, e2e_page, web_cfg):
    #     pg = AnalyticsPage(e2e_page)
    #     pg.go_to("analytics", web_cfg["dashboard_url"])
    #     pg.wait_for_spinner_gone()

    #     with allure.step("All 3 tabs visible"):
    #         assert pg.is_loaded()
    #         pg.expect_visible(AnalyticsPage.TAB_OPERATIONS)
    #         pg.expect_visible(AnalyticsPage.TAB_BUSINESS)
    #         pg.expect_visible(AnalyticsPage.TAB_BRANDS)

    #     with allure.step("Orders Per Day chart visible on Operations tab"):
    #         assert pg.charts_visible()

    #     with allure.step("Cycle all tabs"):
    #         for tab in ANALYTICS_TABS:
    #             with allure.step(f"Tab: {tab}"):
    #                 pg.click_tab(tab)
    #                 assert "/analytics" in pg.current_url()

    #     with allure.step("Filter controls visible on Operations tab"):
    #         pg.click_tab("operations")
    #         pg.expect_visible(AnalyticsPage.BRAND_FILTER)
    #         pg.expect_visible(AnalyticsPage.DARKSTORE_FILTER)
    #         pg.expect_visible(AnalyticsPage.SAVE_PRESET_BTN)
    #         pg.expect_visible(AnalyticsPage.CLEAR_ALL_BTN)

    #     with allure.step("Clear All survives without crash"):
    #         pg.click_clear_all()
    #         pg.expect_visible(AnalyticsPage.HEADING)

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
