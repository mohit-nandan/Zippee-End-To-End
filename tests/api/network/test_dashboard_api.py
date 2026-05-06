"""
Network interception tests — API validation followed by UI assertion on the same page.

Flow for every test:
  1. Watch API endpoints BEFORE navigation (interceptor attaches listener)
  2. Navigate to the page (browser fires real fetch calls)
  3. Validate API — status 200, correct schema, correct nested fields
  4. Validate UI   — page elements rendered correctly using the real data

If the API step fails you know it's a backend problem.
If the API passes but UI fails you know it's a frontend rendering problem.

Add endpoint paths to test_data/api_test_data.py as you capture them from DevTools.
Tests with empty endpoint lists are skipped automatically until paths are filled in.
"""
import allure
import pytest

from pages.home_page import HomePage
from pages.brands_page import BrandsPage
from pages.orders_page import OrdersPage
from pages.shipments_page import ShipmentsPage
from pages.deliveries_page import DeliveriesPage
from pages.settlement_page import SettlementPage
from pages.riders_kyc_page import RidersKycPage
from pages.billing_page import BillingPage
from pages.analytics_page import AnalyticsPage
from pages.rules_page import RulesPage
from pages.manual_upload_page import ManualUploadPage
from utils.schema_validator import assert_schema
from test_data.api_test_data import (
    DASHBOARD_ENDPOINTS,
    HOME_KPI_FIELDS,
    HOME_USER_FIELDS,
    HOME_BRAND_ITEM_FIELDS,
    BRANDS_PAGINATION_FIELDS,
    BRANDS_ITEM_FIELDS,
)


def _validate_endpoints(interceptor, endpoints):
    """Assert every endpoint was called, returned 200, keys present, schema valid."""
    for ep in endpoints:
        interceptor.assert_called(ep["path"])
        interceptor.assert_status(ep["path"], 200)
        interceptor.assert_no_server_errors()
        for key in ep["expected_keys"]:
            interceptor.assert_response_key(ep["path"], key)
        if ep.get("schema"):
            call = interceptor.get(ep["path"])
            assert_schema(call.response_body, ep["schema"], label=ep["path"])


def _watch_navigate_validate(interceptor, network_page, endpoints, navigate_fn):
    """Watch endpoints, navigate, validate — shared helper for stub tests."""
    interceptor.watch(*[ep["path"] for ep in endpoints])
    navigate_fn()
    network_page.wait_for_load_state("domcontentloaded")
    _validate_endpoints(interceptor, endpoints)


@allure.feature("Network API Validation + UI")
@pytest.mark.api
@pytest.mark.web
class TestDashboardNetworkAPI:

    # ── Home Dashboard ────────────────────────────────────────────────────────

    @allure.story("Home")
    @allure.title("Home: API validates → then UI elements confirmed on same page")
    def test_home_api(self, network_page, interceptor, web_cfg):
        endpoints = DASHBOARD_ENDPOINTS["home"]
        assert endpoints, "No endpoints defined for 'home' in api_test_data.py"

        # ── Step 1: watch before navigating ──────────────────────────────────
        paths = [ep["path"] for ep in endpoints]
        interceptor.watch(*paths)

        # ── Step 2: navigate ─────────────────────────────────────────────────
        pg = HomePage(network_page)
        with allure.step("Navigate to Home dashboard"):
            pg.go_to("home", web_cfg["dashboard_url"])
            network_page.wait_for_load_state("domcontentloaded")

        # ── Step 3: API validation ────────────────────────────────────────────
        with allure.step("API — all 3 endpoints called with HTTP 200"):
            _validate_endpoints(interceptor, endpoints)

        with allure.step("API — /home/ KPI fields present"):
            kpi = interceptor.get("/api/1/home/").response_body["data"]["kpi"]
            for field in HOME_KPI_FIELDS:
                assert field in kpi, f"KPI missing field '{field}'"

        with allure.step("API — /auth/user/ identity fields present"):
            user_data = interceptor.get("/api/1/auth/user/").response_body["data"]
            for field in HOME_USER_FIELDS:
                assert field in user_data, f"User data missing field '{field}'"

        with allure.step("API — /brands/options/ non-empty list with correct item shape"):
            brands = interceptor.get("/api/1/brands/options/").response_body["data"]
            assert isinstance(brands, list) and len(brands) > 0, \
                "brands/options returned empty list"
            for field in HOME_BRAND_ITEM_FIELDS:
                assert field in brands[0], f"Brand item missing field '{field}'"

        with allure.step("API — at least one active brand (status=true)"):
            assert any(b["status"] is True for b in brands), \
                "No active brands in brands/options response"

        # ── Step 4: UI validation (only reached if all API steps passed) ─────
        with allure.step("UI — page spinner gone, stat cards visible"):
            pg.wait_for_spinner_gone()
            assert pg.is_loaded(), "Home stat card not visible after API confirmed success"

        with allure.step("UI — New Orders card visible"):
            pg.expect_visible(HomePage.NEW_ORDERS_CARD)

        with allure.step("UI — Prepaid Orders card visible"):
            pg.expect_visible(HomePage.PREPAID_CARD)

        with allure.step("UI — Delivered Orders card visible"):
            pg.expect_visible(HomePage.DELIVERED_CARD)

        with allure.step("UI — Coverage map section visible"):
            assert pg.is_coverage_section_visible(), \
                "Coverage map section not visible after API confirmed success"

    # ── Brands ────────────────────────────────────────────────────────────────

    @allure.story("Brands")
    @allure.title("Brands: API validates pagination + item shape → then UI table confirmed")
    def test_brands_api(self, network_page, interceptor, web_cfg):
        endpoints = DASHBOARD_ENDPOINTS["brands"]
        assert endpoints, "No endpoints defined for 'brands' in api_test_data.py"

        # ── Step 1: watch before navigating ──────────────────────────────────
        interceptor.watch(*[ep["path"] for ep in endpoints])

        # ── Step 2: navigate ─────────────────────────────────────────────────
        pg = BrandsPage(network_page)
        with allure.step("Navigate to Brands page"):
            pg.go_to("brands", web_cfg["dashboard_url"])
            network_page.wait_for_load_state("domcontentloaded")

        # ── Step 3: API validation ────────────────────────────────────────────
        with allure.step("API — /brands/ called with HTTP 200 and envelope keys"):
            _validate_endpoints(interceptor, endpoints)

        with allure.step("API — response contains pagination fields"):
            data = interceptor.get("/api/1/brands/").response_body["data"]
            for field in BRANDS_PAGINATION_FIELDS:
                assert field in data, f"Brands data missing pagination field '{field}'"

        with allure.step("API — total > 0 and results list is non-empty"):
            assert data["total"] > 0, "Brands API returned total=0"
            assert isinstance(data["results"], list) and len(data["results"]) > 0, \
                "Brands API results list is empty"

        with allure.step("API — first result item has correct shape"):
            first = data["results"][0]
            for field in BRANDS_ITEM_FIELDS:
                assert field in first, f"Brand item missing field '{field}'"

        with allure.step("API — pagination metadata is consistent"):
            assert data["total_pages"] >= 1, "total_pages should be at least 1"
            assert data["page"] == 1, "First page load should return page=1"
            assert data["page_size"] > 0, "page_size should be positive"

        # ── Step 4: UI validation ─────────────────────────────────────────────
        with allure.step("UI — page heading visible"):
            assert pg.is_loaded(), "Brands heading not visible after API confirmed success"

        with allure.step("UI — table has rows matching API page_size"):
            row_count = pg.get_row_count()
            assert row_count > 0, "Brands table has no rows despite API returning results"
            assert row_count <= data["page_size"], \
                f"UI shows {row_count} rows but page_size is {data['page_size']}"

        with allure.step("UI — Add Brand button visible"):
            pg.expect_visible(BrandsPage.ADD_BRAND_BTN)

    # ── Remaining pages (stubs — fill paths in api_test_data.py) ─────────────

    @allure.story("Orders")
    def test_orders_api(self, network_page, interceptor, web_cfg):
        endpoints = DASHBOARD_ENDPOINTS["orders"]
        if not endpoints:
            pytest.skip("No endpoints defined for 'orders' — add paths to api_test_data.py")
        _watch_navigate_validate(interceptor, network_page, endpoints,
            lambda: OrdersPage(network_page).go_to("orders", web_cfg["dashboard_url"]))

    @allure.story("Shipments")
    def test_shipments_api(self, network_page, interceptor, web_cfg):
        endpoints = DASHBOARD_ENDPOINTS["shipments"]
        if not endpoints:
            pytest.skip("No endpoints defined for 'shipments' — add paths to api_test_data.py")
        _watch_navigate_validate(interceptor, network_page, endpoints,
            lambda: ShipmentsPage(network_page).go_to("shipments", web_cfg["dashboard_url"]))

    @allure.story("Deliveries PND")
    def test_deliveries_api(self, network_page, interceptor, web_cfg):
        endpoints = DASHBOARD_ENDPOINTS["deliveries"]
        if not endpoints:
            pytest.skip("No endpoints defined for 'deliveries' — add paths to api_test_data.py")
        _watch_navigate_validate(interceptor, network_page, endpoints,
            lambda: DeliveriesPage(network_page).go_to("deliveries", web_cfg["dashboard_url"]))

    @allure.story("Settlement")
    def test_settlement_api(self, network_page, interceptor, web_cfg):
        endpoints = DASHBOARD_ENDPOINTS["settlement"]
        if not endpoints:
            pytest.skip("No endpoints defined for 'settlement' — add paths to api_test_data.py")
        _watch_navigate_validate(interceptor, network_page, endpoints,
            lambda: SettlementPage(network_page).go_to("settlement", web_cfg["dashboard_url"]))

    @allure.story("Riders KYC")
    def test_riders_kyc_api(self, network_page, interceptor, web_cfg):
        endpoints = DASHBOARD_ENDPOINTS["riders_kyc"]
        if not endpoints:
            pytest.skip("No endpoints defined for 'riders_kyc' — add paths to api_test_data.py")
        _watch_navigate_validate(interceptor, network_page, endpoints,
            lambda: RidersKycPage(network_page).go_to("riders_kyc", web_cfg["dashboard_url"]))

    @allure.story("Billing")
    def test_billing_api(self, network_page, interceptor, web_cfg):
        endpoints = DASHBOARD_ENDPOINTS["billing"]
        if not endpoints:
            pytest.skip("No endpoints defined for 'billing' — add paths to api_test_data.py")
        _watch_navigate_validate(interceptor, network_page, endpoints,
            lambda: BillingPage(network_page).go_to("billing", web_cfg["dashboard_url"]))

    @allure.story("Analytics")
    def test_analytics_api(self, network_page, interceptor, web_cfg):
        endpoints = DASHBOARD_ENDPOINTS["analytics"]
        if not endpoints:
            pytest.skip("No endpoints defined for 'analytics' — add paths to api_test_data.py")
        _watch_navigate_validate(interceptor, network_page, endpoints,
            lambda: AnalyticsPage(network_page).go_to("analytics", web_cfg["dashboard_url"]))

    @allure.story("Rules")
    def test_rules_api(self, network_page, interceptor, web_cfg):
        endpoints = DASHBOARD_ENDPOINTS["rules"]
        if not endpoints:
            pytest.skip("No endpoints defined for 'rules' — add paths to api_test_data.py")
        _watch_navigate_validate(interceptor, network_page, endpoints,
            lambda: RulesPage(network_page).go_to("rules", web_cfg["dashboard_url"]))

    @allure.story("Manual Upload")
    def test_manual_upload_api(self, network_page, interceptor, web_cfg):
        endpoints = DASHBOARD_ENDPOINTS["manual_upload"]
        if not endpoints:
            pytest.skip("No endpoints defined for 'manual_upload' — add paths to api_test_data.py")
        _watch_navigate_validate(interceptor, network_page, endpoints,
            lambda: ManualUploadPage(network_page).go_to("manual_upload", web_cfg["dashboard_url"]))
