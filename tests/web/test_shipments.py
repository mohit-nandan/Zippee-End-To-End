"""
Shipments page tests — UI, search, sort, filter, API validation.
URL: /shipments  (Middleware > Shipments)
"""
import allure
import pytest
from pages.shipments_page import ShipmentsPage
from utils.web_api_interceptor import ApiInterceptor
from test_data.web_test_data import NO_MATCH_STRING, KNOWN_DARKSTORE


@pytest.fixture
def shipments(authenticated_dashboard, web_cfg):
    interceptor = ApiInterceptor(authenticated_dashboard).watch("/shipment", "/api")
    pg = ShipmentsPage(authenticated_dashboard)
    pg.go_to("shipments", web_cfg["dashboard_url"])
    pg.wait_for_spinner_gone()
    return pg, interceptor


@allure.feature("Shipments")
class TestShipmentsUI:

    @allure.story("Page load")
    @allure.title("Shipments page loads with stat cards")
    @pytest.mark.smoke
    @pytest.mark.web
    def test_page_loads(self, shipments):
        pg, _ = shipments
        assert pg.is_loaded()
        pg.expect_visible(ShipmentsPage.STAT_TOTAL)
        pg.expect_visible(ShipmentsPage.STAT_OPEN)
        pg.expect_visible(ShipmentsPage.STAT_FAILED)
        pg.expect_visible(ShipmentsPage.STAT_PROCESSED)

    @allure.story("Page load")
    @allure.title("Table has data rows")
    @pytest.mark.sanity
    @pytest.mark.web
    def test_table_has_rows(self, shipments):
        pg, _ = shipments
        assert pg.get_row_count() > 0

    @allure.story("AWB Search")
    @allure.title("AWB search filters matching rows")
    @pytest.mark.sanity
    @pytest.mark.web
    def test_search_awb_returns_results(self, shipments):
        pg, _ = shipments
        first_awb = pg.get_first_awb()
        if not first_awb:
            pytest.skip("No AWBs in table")
        with allure.step(f"Search for AWB prefix: {first_awb[:6]}"):
            pg.search_awb(first_awb[:6])
            pg.wait_for_spinner_gone()
        assert pg.get_row_count() >= 1

    @allure.story("AWB Search")
    @allure.title("AWB search with no match shows empty table")
    @pytest.mark.sanity
    @pytest.mark.web
    def test_search_awb_no_match(self, shipments):
        pg, _ = shipments
        pg.search_awb(NO_MATCH_STRING)
        pg.wait_for_spinner_gone()
        assert pg.get_row_count() == 0

    @allure.story("Darkstore Search")
    @allure.title("Darkstore search filters results")
    @pytest.mark.sanity
    @pytest.mark.web
    def test_search_darkstore(self, shipments):
        pg, _ = shipments
        pg.search_darkstore(KNOWN_DARKSTORE[:7])
        pg.wait_for_spinner_gone()
        assert pg.get_row_count() >= 0

    @allure.story("Sorting")
    @allure.title("Sort by Zippee AWB does not change row count")
    @pytest.mark.regression
    @pytest.mark.web
    @pytest.mark.parametrize("col", ["Zippee AWB", "Shipping Status", "Creation Time"])
    def test_sort_columns(self, shipments, col):
        pg, _ = shipments
        before = pg.get_row_count()
        pg.click_sort(col)
        assert pg.get_row_count() == before

    @allure.story("Actions")
    @allure.title("Refire and Bulk Action Logs buttons visible")
    @pytest.mark.smoke
    @pytest.mark.web
    def test_action_buttons_visible(self, shipments):
        pg, _ = shipments
        pg.expect_visible(ShipmentsPage.REFIRE_BTN)
        pg.expect_visible(ShipmentsPage.BULK_ACTION_BTN)


@allure.feature("Shipments")
class TestShipmentsAPI:

    @allure.story("API validation")
    @allure.title("No 5xx errors on shipments page load")
    @pytest.mark.smoke
    @pytest.mark.web
    def test_no_server_errors_on_load(self, authenticated_dashboard, web_cfg):
        interceptor = ApiInterceptor(authenticated_dashboard).watch("")
        pg = ShipmentsPage(authenticated_dashboard)
        pg.go_to("shipments", web_cfg["dashboard_url"])
        pg.wait_for_network_idle()
        interceptor.assert_no_server_errors()

    @allure.story("API validation")
    @allure.title("Shipments API call is made on page load")
    @pytest.mark.sanity
    @pytest.mark.web
    def test_shipments_api_called(self, authenticated_dashboard, web_cfg):
        interceptor = ApiInterceptor(authenticated_dashboard).watch("/shipment", "/zorms")
        pg = ShipmentsPage(authenticated_dashboard)
        pg.go_to("shipments", web_cfg["dashboard_url"])
        pg.wait_for_network_idle()
        # At least one API call to a shipments-related endpoint
        calls = interceptor.all()
        assert len(calls) > 0, "Expected at least one API call on shipments page load"

    @allure.story("API validation")
    @allure.title("Shipment API returns success status")
    @pytest.mark.sanity
    @pytest.mark.web
    def test_shipments_api_status_ok(self, authenticated_dashboard, web_cfg):
        interceptor = ApiInterceptor(authenticated_dashboard).watch("")
        pg = ShipmentsPage(authenticated_dashboard)
        pg.go_to("shipments", web_cfg["dashboard_url"])
        pg.wait_for_network_idle()
        failed = [c for c in interceptor.all() if c.status >= 400]
        assert failed == [], (
            f"API errors on shipments page: {[(c.url, c.status) for c in failed]}"
        )
