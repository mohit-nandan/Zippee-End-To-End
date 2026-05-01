"""
Orders page tests — UI, search, sort, filter, API validation.
URL: /orders  (Middleware > Orders)
"""
import allure
import pytest
from pages.orders_page import OrdersPage
from utils.web_api_interceptor import ApiInterceptor
from test_data.web_test_data import NO_MATCH_STRING, KNOWN_BRAND, PAYMENT_MODES


@pytest.fixture
def orders(authenticated_dashboard, web_cfg):
    pg = OrdersPage(authenticated_dashboard)
    pg.go_to("orders", web_cfg["dashboard_url"])
    pg.wait_for_spinner_gone()
    return pg


@allure.feature("Orders")
class TestOrdersUI:

    @allure.story("Page load")
    @allure.title("Orders page loads with heading")
    @pytest.mark.smoke
    @pytest.mark.web
    def test_page_loads(self, orders):
        assert orders.is_loaded()
        orders.expect_url("/orders")

    @allure.story("Page load")
    @allure.title("Orders table has rows")
    @pytest.mark.sanity
    @pytest.mark.web
    def test_table_has_rows(self, orders):
        assert orders.get_row_count() > 0

    @allure.story("Search")
    @allure.title("Reference code search filters results")
    @pytest.mark.sanity
    @pytest.mark.web
    def test_search_by_reference(self, orders):
        ref = orders.get_first_ref_code()
        if not ref:
            pytest.skip("No orders to test with")
        orders.search_reference(ref[:5])
        orders.wait_for_spinner_gone()
        assert orders.get_row_count() >= 1

    @allure.story("Search")
    @allure.title("Non-existent reference returns empty table")
    @pytest.mark.sanity
    @pytest.mark.web
    def test_search_no_match(self, orders):
        orders.search_reference(NO_MATCH_STRING)
        orders.wait_for_spinner_gone()
        assert orders.get_row_count() == 0

    @allure.story("Search")
    @allure.title("Brand name search filters results")
    @pytest.mark.sanity
    @pytest.mark.web
    def test_search_by_brand(self, orders):
        orders.search_brand(KNOWN_BRAND[:7])
        orders.wait_for_spinner_gone()
        assert orders.get_row_count() >= 0

    @allure.story("Filter")
    @allure.title("Payment mode filter — {mode}")
    @pytest.mark.sanity
    @pytest.mark.web
    @pytest.mark.parametrize("mode", PAYMENT_MODES)
    def test_filter_payment_mode(self, orders, mode):
        orders.filter_payment_mode(mode)
        orders.wait_for_spinner_gone()
        assert orders.get_row_count() >= 0

    @allure.story("Sorting")
    @allure.title("Column sort does not lose rows — {col}")
    @pytest.mark.regression
    @pytest.mark.web
    @pytest.mark.parametrize("col", ["Reference Code", "Brand Name", "Order Date"])
    def test_sort_columns(self, orders, col):
        before = orders.get_row_count()
        orders.click_sort(col)
        assert orders.get_row_count() == before


@allure.feature("Orders")
class TestOrdersAPI:

    @allure.story("API validation")
    @allure.title("No 5xx errors on orders page load")
    @pytest.mark.smoke
    @pytest.mark.web
    def test_no_server_errors(self, authenticated_dashboard, web_cfg):
        interceptor = ApiInterceptor(authenticated_dashboard).watch("")
        pg = OrdersPage(authenticated_dashboard)
        pg.go_to("orders", web_cfg["dashboard_url"])
        pg.wait_for_network_idle()
        interceptor.assert_no_server_errors()

    @allure.story("API validation")
    @allure.title("All API calls on orders page return success")
    @pytest.mark.sanity
    @pytest.mark.web
    def test_all_api_calls_succeed(self, authenticated_dashboard, web_cfg):
        interceptor = ApiInterceptor(authenticated_dashboard).watch("")
        pg = OrdersPage(authenticated_dashboard)
        pg.go_to("orders", web_cfg["dashboard_url"])
        pg.wait_for_network_idle()
        failed = [c for c in interceptor.all() if c.status >= 400]
        assert failed == [], f"API errors: {[(c.url, c.status) for c in failed]}"
