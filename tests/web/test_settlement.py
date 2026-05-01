"""
Settlement page tests — tabs, API validation.
URL: /settlement  (COD > Settlements)
"""
import allure
import pytest
from pages.settlement_page import SettlementPage
from utils.web_api_interceptor import ApiInterceptor
from test_data.web_test_data import SETTLEMENT_TABS


@pytest.fixture
def settlement(authenticated_dashboard, web_cfg):
    pg = SettlementPage(authenticated_dashboard)
    pg.go_to("settlement", web_cfg["dashboard_url"])
    pg.wait_for_spinner_gone()
    return pg


@allure.feature("Settlement")
class TestSettlementUI:

    @allure.story("Page load")
    @allure.title("Settlement page loads with all 4 tabs")
    @pytest.mark.smoke
    @pytest.mark.web
    def test_page_loads(self, settlement):
        assert settlement.is_loaded()
        settlement.expect_visible(SettlementPage.TAB_RIDER)
        settlement.expect_visible(SettlementPage.TAB_DARKSTORE)
        settlement.expect_visible(SettlementPage.TAB_COMPANY)
        settlement.expect_visible(SettlementPage.TAB_BRAND)

    @allure.story("Tabs")
    @allure.title("Tab switch works — {tab}")
    @pytest.mark.sanity
    @pytest.mark.web
    @pytest.mark.parametrize("tab", SETTLEMENT_TABS)
    def test_tab_switch(self, settlement, tab):
        settlement.click_tab(tab)
        settlement.wait_for_spinner_gone()
        assert "/settlement" in settlement.current_url()

    @allure.story("Rider view")
    @allure.title("Rider toggle is visible on Rider tab")
    @pytest.mark.sanity
    @pytest.mark.web
    def test_rider_toggle_visible(self, settlement):
        settlement.expect_visible(SettlementPage.TOGGLE_RIDER)


@allure.feature("Settlement")
class TestSettlementAPI:

    @allure.story("API validation")
    @allure.title("No 5xx errors on settlement page")
    @pytest.mark.smoke
    @pytest.mark.web
    def test_no_server_errors(self, authenticated_dashboard, web_cfg):
        interceptor = ApiInterceptor(authenticated_dashboard).watch("")
        pg = SettlementPage(authenticated_dashboard)
        pg.go_to("settlement", web_cfg["dashboard_url"])
        pg.wait_for_network_idle()
        interceptor.assert_no_server_errors()

    @allure.story("API validation")
    @allure.title("Settlement API calls succeed on tab switch")
    @pytest.mark.sanity
    @pytest.mark.web
    def test_api_on_tab_switch(self, authenticated_dashboard, web_cfg):
        interceptor = ApiInterceptor(authenticated_dashboard).watch("")
        pg = SettlementPage(authenticated_dashboard)
        pg.go_to("settlement", web_cfg["dashboard_url"])
        pg.wait_for_spinner_gone()
        pg.click_tab("dark_store")
        pg.wait_for_network_idle()
        failed = [c for c in interceptor.all() if c.status >= 400]
        assert failed == [], f"API errors on settlement tab switch: {[(c.url, c.status) for c in failed]}"
