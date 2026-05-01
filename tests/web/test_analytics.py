"""
Analytics page tests — tabs, filters, API validation.
URL: /analytics
"""
import allure
import pytest
from pages.analytics_page import AnalyticsPage
from utils.web_api_interceptor import ApiInterceptor
from test_data.web_test_data import ANALYTICS_TABS


@pytest.fixture
def analytics(authenticated_dashboard, web_cfg):
    pg = AnalyticsPage(authenticated_dashboard)
    pg.go_to("analytics", web_cfg["dashboard_url"])
    pg.wait_for_spinner_gone()
    return pg


@allure.feature("Analytics")
class TestAnalyticsUI:

    @allure.story("Page load")
    @allure.title("Analytics page loads with all 3 tabs")
    @pytest.mark.smoke
    @pytest.mark.web
    def test_page_loads(self, analytics):
        assert analytics.is_loaded()
        analytics.expect_visible(AnalyticsPage.TAB_OPERATIONS)
        analytics.expect_visible(AnalyticsPage.TAB_BUSINESS)
        analytics.expect_visible(AnalyticsPage.TAB_BRANDS)

    @allure.story("Charts")
    @allure.title("Operations tab shows Orders Per Day chart")
    @pytest.mark.smoke
    @pytest.mark.web
    def test_operations_chart_visible(self, analytics):
        assert analytics.charts_visible()

    @allure.story("Tabs")
    @allure.title("Tab switch works — {tab}")
    @pytest.mark.sanity
    @pytest.mark.web
    @pytest.mark.parametrize("tab", ANALYTICS_TABS)
    def test_tab_switch(self, analytics, tab):
        analytics.click_tab(tab)
        analytics.wait_for_spinner_gone()
        assert "/analytics" in analytics.current_url()

    @allure.story("Filters")
    @allure.title("Brand and Darkstore filter dropdowns are visible")
    @pytest.mark.sanity
    @pytest.mark.web
    def test_filters_visible(self, analytics):
        analytics.expect_visible(AnalyticsPage.BRAND_FILTER)
        analytics.expect_visible(AnalyticsPage.DARKSTORE_FILTER)

    @allure.story("Filters")
    @allure.title("Save Preset and Clear All buttons are visible")
    @pytest.mark.sanity
    @pytest.mark.web
    def test_preset_controls_visible(self, analytics):
        analytics.expect_visible(AnalyticsPage.SAVE_PRESET_BTN)
        analytics.expect_visible(AnalyticsPage.CLEAR_ALL_BTN)

    @allure.story("Filters")
    @allure.title("Clear All resets without crashing")
    @pytest.mark.regression
    @pytest.mark.web
    def test_clear_all_works(self, analytics):
        analytics.click_clear_all()
        analytics.expect_visible(AnalyticsPage.HEADING)


@allure.feature("Analytics")
class TestAnalyticsAPI:

    @allure.story("API validation")
    @allure.title("No 5xx errors on analytics page")
    @pytest.mark.smoke
    @pytest.mark.web
    def test_no_server_errors(self, authenticated_dashboard, web_cfg):
        interceptor = ApiInterceptor(authenticated_dashboard).watch("")
        pg = AnalyticsPage(authenticated_dashboard)
        pg.go_to("analytics", web_cfg["dashboard_url"])
        pg.wait_for_network_idle()
        interceptor.assert_no_server_errors()

    @allure.story("API validation")
    @allure.title("Analytics API calls succeed on tab switch")
    @pytest.mark.sanity
    @pytest.mark.web
    def test_api_on_tab_switch(self, authenticated_dashboard, web_cfg):
        interceptor = ApiInterceptor(authenticated_dashboard).watch("")
        pg = AnalyticsPage(authenticated_dashboard)
        pg.go_to("analytics", web_cfg["dashboard_url"])
        pg.wait_for_spinner_gone()
        pg.click_tab("business")
        pg.wait_for_network_idle()
        failed = [c for c in interceptor.all() if c.status >= 400]
        assert failed == [], f"API errors on analytics tab switch: {[(c.url, c.status) for c in failed]}"
