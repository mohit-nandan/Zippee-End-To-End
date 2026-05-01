"""
Brands page tests — UI, search, sort, API validation.
URL: /brand
"""
import allure
import pytest
from pages.brands_page import BrandsPage
from utils.web_api_interceptor import ApiInterceptor
from test_data.web_test_data import NO_MATCH_STRING


@pytest.fixture
def brands(authenticated_dashboard, web_cfg):
    pg = BrandsPage(authenticated_dashboard)
    pg.go_to("brands", web_cfg["dashboard_url"])
    pg.wait_for_spinner_gone()
    return pg


@allure.feature("Brands")
class TestBrandsUI:

    @allure.story("Page load")
    @allure.title("Brands page loads with table and Add Brand button")
    @pytest.mark.smoke
    @pytest.mark.web
    def test_page_loads(self, brands):
        assert brands.is_loaded()
        brands.expect_visible(BrandsPage.ADD_BRAND_BTN)

    @allure.story("Page load")
    @allure.title("Brands table has data rows")
    @pytest.mark.sanity
    @pytest.mark.web
    def test_table_has_rows(self, brands):
        assert brands.get_row_count() > 0

    @allure.story("Search")
    @allure.title("Brand name search filters matching results")
    @pytest.mark.sanity
    @pytest.mark.web
    def test_search_by_name_matches(self, brands):
        name = brands.get_first_brand_name()
        if not name:
            pytest.skip("No brands in table")
        with allure.step(f"Searching for: {name[:4]}"):
            brands.search_column("brand_name", name[:4])
            brands.wait_for_spinner_gone()
        assert brands.get_row_count() >= 1

    @allure.story("Search")
    @allure.title("Brand name search with no match shows empty table")
    @pytest.mark.sanity
    @pytest.mark.web
    def test_search_no_match(self, brands):
        brands.search_column("brand_name", NO_MATCH_STRING)
        brands.wait_for_spinner_gone()
        assert brands.get_row_count() == 0

    @allure.story("Search")
    @allure.title("Clearing search restores all results")
    @pytest.mark.sanity
    @pytest.mark.web
    def test_clear_search_restores(self, brands):
        brands.search_column("brand_name", NO_MATCH_STRING)
        brands.wait_for_spinner_gone()
        brands.clear_search("brand_name")
        brands.wait_for_spinner_gone()
        assert brands.get_row_count() > 0

    @allure.story("Sorting")
    @allure.title("Column sort does not change row count")
    @pytest.mark.regression
    @pytest.mark.web
    @pytest.mark.parametrize("col", ["Brand Name", "Wallet Balance", "Category", "Last Recharge Date"])
    def test_sort_columns(self, brands, col):
        before = brands.get_row_count()
        brands.click_sort(col)
        assert brands.get_row_count() == before

    @allure.story("URL")
    @allure.title("Brands page URL is /brand")
    @pytest.mark.smoke
    @pytest.mark.web
    def test_url_correct(self, brands):
        brands.expect_url("/brand")


@allure.feature("Brands")
class TestBrandsAPI:

    @allure.story("API validation")
    @allure.title("No 5xx errors on brands page load")
    @pytest.mark.smoke
    @pytest.mark.web
    def test_no_server_errors(self, authenticated_dashboard, web_cfg):
        interceptor = ApiInterceptor(authenticated_dashboard).watch("")
        pg = BrandsPage(authenticated_dashboard)
        pg.go_to("brands", web_cfg["dashboard_url"])
        pg.wait_for_network_idle()
        interceptor.assert_no_server_errors()

    @allure.story("API validation")
    @allure.title("Brands API call returns success response")
    @pytest.mark.sanity
    @pytest.mark.web
    def test_brands_api_success(self, authenticated_dashboard, web_cfg):
        interceptor = ApiInterceptor(authenticated_dashboard).watch("")
        pg = BrandsPage(authenticated_dashboard)
        pg.go_to("brands", web_cfg["dashboard_url"])
        pg.wait_for_network_idle()
        errors = [c for c in interceptor.all() if c.status >= 400]
        assert errors == [], f"API errors: {[(c.url, c.status) for c in errors]}"

    @allure.story("API validation")
    @allure.title("At least one API call is made on brands page")
    @pytest.mark.sanity
    @pytest.mark.web
    def test_api_calls_made(self, authenticated_dashboard, web_cfg):
        interceptor = ApiInterceptor(authenticated_dashboard).watch("")
        pg = BrandsPage(authenticated_dashboard)
        pg.go_to("brands", web_cfg["dashboard_url"])
        pg.wait_for_network_idle()
        assert len(interceptor.all()) > 0
