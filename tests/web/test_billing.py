"""
Billing & Invoices page tests — tabs, sub-tabs, stats, API validation.
URL: /billing
"""
import allure
import pytest
from pages.billing_page import BillingPage
from utils.web_api_interceptor import ApiInterceptor


@pytest.fixture
def billing(authenticated_dashboard, web_cfg):
    pg = BillingPage(authenticated_dashboard)
    pg.go_to("billing", web_cfg["dashboard_url"])
    pg.wait_for_spinner_gone()
    return pg


@allure.feature("Billing & Invoices")
class TestBillingUI:

    @allure.story("Page load")
    @allure.title("Billing page loads with heading and tabs")
    @pytest.mark.smoke
    @pytest.mark.web
    def test_page_loads(self, billing):
        assert billing.is_loaded()
        billing.expect_visible(BillingPage.TAB_DEDUCTIONS)
        billing.expect_visible(BillingPage.TAB_INVOICES)

    @allure.story("Stats")
    @allure.title("Deduction stat cards are visible")
    @pytest.mark.smoke
    @pytest.mark.web
    def test_stats_visible(self, billing):
        assert billing.stats_visible()
        billing.expect_visible(BillingPage.STAT_NUM_DEDUCTIONS)

    @allure.story("Tabs")
    @allure.title("Switch to Invoices tab")
    @pytest.mark.sanity
    @pytest.mark.web
    def test_invoices_tab(self, billing):
        billing.click_tab("invoices")
        billing.expect_visible(BillingPage.TAB_INVOICES)

    @allure.story("Tabs")
    @allure.title("Switch back to Deductions tab")
    @pytest.mark.sanity
    @pytest.mark.web
    def test_deductions_tab_back(self, billing):
        billing.click_tab("invoices")
        billing.click_tab("deductions")
        billing.expect_visible(BillingPage.STAT_TOTAL_USAGE)

    @allure.story("Sub-tabs")
    @allure.title("Daily Summary sub-tab works")
    @pytest.mark.sanity
    @pytest.mark.web
    def test_daily_summary_subtab(self, billing):
        billing.click_subtab("daily")
        billing.expect_visible(BillingPage.SUBTAB_DAILY)

    @allure.story("Sub-tabs")
    @allure.title("Deduction View sub-tab works")
    @pytest.mark.sanity
    @pytest.mark.web
    def test_deduction_view_subtab(self, billing):
        billing.click_subtab("deduction_view")
        billing.expect_visible(BillingPage.SUBTAB_DEDUCTION)

    @allure.story("Actions")
    @allure.title("Generate Invoice, Send Invoices, MG Adjustment buttons visible")
    @pytest.mark.smoke
    @pytest.mark.web
    def test_action_buttons_visible(self, billing):
        billing.expect_visible(BillingPage.GEN_INVOICE_BTN)
        billing.expect_visible(BillingPage.SEND_INVOICES_BTN)
        billing.expect_visible(BillingPage.MG_ADJUSTMENT_BTN)

    @allure.story("Table")
    @allure.title("Deductions table has rows")
    @pytest.mark.sanity
    @pytest.mark.web
    def test_table_has_rows(self, billing):
        assert billing.get_row_count() >= 1


@allure.feature("Billing & Invoices")
class TestBillingAPI:

    @allure.story("API validation")
    @allure.title("No 5xx errors on billing page")
    @pytest.mark.smoke
    @pytest.mark.web
    def test_no_server_errors(self, authenticated_dashboard, web_cfg):
        interceptor = ApiInterceptor(authenticated_dashboard).watch("")
        pg = BillingPage(authenticated_dashboard)
        pg.go_to("billing", web_cfg["dashboard_url"])
        pg.wait_for_network_idle()
        interceptor.assert_no_server_errors()

    @allure.story("API validation")
    @allure.title("All billing API calls return success")
    @pytest.mark.sanity
    @pytest.mark.web
    def test_api_calls_succeed(self, authenticated_dashboard, web_cfg):
        interceptor = ApiInterceptor(authenticated_dashboard).watch("")
        pg = BillingPage(authenticated_dashboard)
        pg.go_to("billing", web_cfg["dashboard_url"])
        pg.wait_for_network_idle()
        failed = [c for c in interceptor.all() if c.status >= 400]
        assert failed == [], f"API errors on billing: {[(c.url, c.status) for c in failed]}"
