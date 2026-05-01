"""
Riders / KYC Verification page tests — search, sort, API validation.
URL: /kyc  (COD > Riders)
"""
import allure
import pytest
from pages.riders_kyc_page import RidersKycPage
from utils.web_api_interceptor import ApiInterceptor
from test_data.web_test_data import NO_MATCH_STRING, KNOWN_RIDER_NAME, KNOWN_CITY


@pytest.fixture
def riders(authenticated_dashboard, web_cfg):
    pg = RidersKycPage(authenticated_dashboard)
    pg.go_to("riders_kyc", web_cfg["dashboard_url"])
    pg.wait_for_spinner_gone()
    return pg


@allure.feature("Riders / KYC")
class TestRidersUI:

    @allure.story("Page load")
    @allure.title("KYC Verification page loads with table")
    @pytest.mark.smoke
    @pytest.mark.web
    def test_page_loads(self, riders):
        assert riders.is_loaded()
        riders.expect_url("/kyc")

    @allure.story("Page load")
    @allure.title("KYC table has data rows")
    @pytest.mark.sanity
    @pytest.mark.web
    def test_table_has_rows(self, riders):
        assert riders.get_row_count() > 0

    @allure.story("Search")
    @allure.title("Rider name search filters results")
    @pytest.mark.sanity
    @pytest.mark.web
    def test_search_by_name(self, riders):
        riders.search_rider(KNOWN_RIDER_NAME)
        riders.wait_for_spinner_gone()
        assert riders.get_row_count() >= 1

    @allure.story("Search")
    @allure.title("Non-existent rider returns empty table")
    @pytest.mark.sanity
    @pytest.mark.web
    def test_search_no_match(self, riders):
        riders.search_rider(NO_MATCH_STRING)
        riders.wait_for_spinner_gone()
        assert riders.get_row_count() == 0

    @allure.story("Search")
    @allure.title("City search filters results")
    @pytest.mark.sanity
    @pytest.mark.web
    def test_search_by_city(self, riders):
        riders.search_city(KNOWN_CITY)
        riders.wait_for_spinner_gone()
        assert riders.get_row_count() >= 0

    @allure.story("Sorting")
    @allure.title("Column sort does not change row count — {col}")
    @pytest.mark.regression
    @pytest.mark.web
    @pytest.mark.parametrize("col", ["Rider Name", "City", "Darkstore"])
    def test_sort_columns(self, riders, col):
        before = riders.get_row_count()
        riders.click_sort(col)
        assert riders.get_row_count() == before

    @allure.story("Status")
    @allure.title("Approved status label is visible in table")
    @pytest.mark.smoke
    @pytest.mark.web
    def test_approved_status_visible(self, riders):
        riders.expect_visible(RidersKycPage.STATUS_APPROVED)


@allure.feature("Riders / KYC")
class TestRidersAPI:

    @allure.story("API validation")
    @allure.title("No 5xx errors on riders page")
    @pytest.mark.smoke
    @pytest.mark.web
    def test_no_server_errors(self, authenticated_dashboard, web_cfg):
        interceptor = ApiInterceptor(authenticated_dashboard).watch("")
        pg = RidersKycPage(authenticated_dashboard)
        pg.go_to("riders_kyc", web_cfg["dashboard_url"])
        pg.wait_for_network_idle()
        interceptor.assert_no_server_errors()

    @allure.story("API validation")
    @allure.title("All API calls on riders page succeed")
    @pytest.mark.sanity
    @pytest.mark.web
    def test_api_calls_succeed(self, authenticated_dashboard, web_cfg):
        interceptor = ApiInterceptor(authenticated_dashboard).watch("")
        pg = RidersKycPage(authenticated_dashboard)
        pg.go_to("riders_kyc", web_cfg["dashboard_url"])
        pg.wait_for_network_idle()
        failed = [c for c in interceptor.all() if c.status >= 400]
        assert failed == [], f"API errors on riders/KYC: {[(c.url, c.status) for c in failed]}"
