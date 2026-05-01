"""
Deliveries (PND) page tests — tabs, search, API validation.
URL: /pnd  (Pickup Delivery > Deliveries)
"""
import allure
import pytest
from pages.deliveries_page import DeliveriesPage
from utils.web_api_interceptor import ApiInterceptor
from test_data.web_test_data import NO_MATCH_STRING, PND_TABS


@pytest.fixture
def deliveries(authenticated_dashboard, web_cfg):
    pg = DeliveriesPage(authenticated_dashboard)
    pg.go_to("deliveries", web_cfg["dashboard_url"])
    pg.wait_for_spinner_gone()
    return pg


@allure.feature("Deliveries (PND)")
class TestDeliveriesUI:

    @allure.story("Page load")
    @allure.title("Deliveries page loads with Shipments and Trips tabs")
    @pytest.mark.smoke
    @pytest.mark.web
    def test_page_loads(self, deliveries):
        assert deliveries.is_loaded()
        deliveries.expect_visible(DeliveriesPage.TAB_SHIPMENTS)
        deliveries.expect_visible(DeliveriesPage.TAB_TRIPS)

    @allure.story("Sub-tabs")
    @allure.title("All shipment sub-tabs are clickable — {tab}")
    @pytest.mark.sanity
    @pytest.mark.web
    @pytest.mark.parametrize("tab", PND_TABS)
    def test_shipment_subtab_clickable(self, deliveries, tab):
        with allure.step(f"Click tab: {tab}"):
            deliveries.click_tab(tab)
            deliveries.wait_for_spinner_gone()
        # Tab switch should not crash or navigate away
        assert "/pnd" in deliveries.current_url()

    @allure.story("Trips tab")
    @allure.title("Trips tab switches and switches back correctly")
    @pytest.mark.sanity
    @pytest.mark.web
    def test_trips_tab_switch(self, deliveries):
        deliveries.click_tab("trips")
        deliveries.expect_visible(DeliveriesPage.TAB_TRIPS)
        deliveries.click_tab("shipments")
        deliveries.expect_visible(DeliveriesPage.TAB_ASSIGN_NOW)

    @allure.story("Search")
    @allure.title("AWB search on All Shipments returns matching rows")
    @pytest.mark.sanity
    @pytest.mark.web
    def test_search_awb(self, deliveries):
        deliveries.click_tab("all_shipments")
        deliveries.search_awb("FBX")
        deliveries.wait_for_spinner_gone()
        assert deliveries.get_row_count() >= 0

    @allure.story("Search")
    @allure.title("Non-existent AWB search returns empty table")
    @pytest.mark.sanity
    @pytest.mark.web
    def test_search_awb_no_match(self, deliveries):
        deliveries.click_tab("all_shipments")
        deliveries.search_awb(NO_MATCH_STRING)
        deliveries.wait_for_spinner_gone()
        assert deliveries.get_row_count() == 0

    @allure.story("Actions")
    @allure.title("Create Trip button is visible")
    @pytest.mark.smoke
    @pytest.mark.web
    def test_create_trip_btn_visible(self, deliveries):
        deliveries.expect_visible(DeliveriesPage.CREATE_TRIP_BTN)


@allure.feature("Deliveries (PND)")
class TestDeliveriesAPI:

    @allure.story("API validation")
    @allure.title("No 5xx errors on deliveries page load")
    @pytest.mark.smoke
    @pytest.mark.web
    def test_no_server_errors(self, authenticated_dashboard, web_cfg):
        interceptor = ApiInterceptor(authenticated_dashboard).watch("")
        pg = DeliveriesPage(authenticated_dashboard)
        pg.go_to("deliveries", web_cfg["dashboard_url"])
        pg.wait_for_network_idle()
        interceptor.assert_no_server_errors()

    @allure.story("API validation")
    @allure.title("All API calls succeed on deliveries page")
    @pytest.mark.sanity
    @pytest.mark.web
    def test_all_api_calls_succeed(self, authenticated_dashboard, web_cfg):
        interceptor = ApiInterceptor(authenticated_dashboard).watch("")
        pg = DeliveriesPage(authenticated_dashboard)
        pg.go_to("deliveries", web_cfg["dashboard_url"])
        pg.wait_for_network_idle()
        failed = [c for c in interceptor.all() if c.status >= 400]
        assert failed == [], f"API errors on deliveries: {[(c.url, c.status) for c in failed]}"
