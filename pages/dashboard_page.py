from pages.base_page import BasePage
from pages.order_list_page import OrderListPage


class DashboardPage(BasePage):
    """Update selectors to match your actual dashboard HTML."""
    NAV_ORDERS = "a[href='/orders'], nav a:has-text('Orders')"
    STATS_CARD = ".stats-card, [data-testid='stats']"

    def go_to_orders(self) -> OrderListPage:
        self.click(self.NAV_ORDERS)
        self.page.wait_for_load_state("networkidle")
        return OrderListPage(self.page)

    def is_loaded(self) -> bool:
        return self.is_visible(self.STATS_CARD) or "/dashboard" in self.page.url
