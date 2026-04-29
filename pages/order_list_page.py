from pages.base_page import BasePage
from pages.order_detail_page import OrderDetailPage


class OrderListPage(BasePage):
    """Update selectors to match your actual orders table HTML."""
    SEARCH_INPUT = "input[placeholder*='Search'], input[name='search']"
    ORDER_ROW    = "table tbody tr, .order-row"
    FIRST_ORDER  = "table tbody tr:first-child, .order-row:first-child"
    STATUS_BADGE = ".status-badge, [data-testid='order-status']"

    def search_order(self, order_ref: str):
        self.fill(self.SEARCH_INPUT, order_ref)
        self.page.keyboard.press("Enter")
        self.page.wait_for_load_state("networkidle")

    def get_first_order_status(self) -> str:
        return self.get_text(f"{self.FIRST_ORDER} {self.STATUS_BADGE}")

    def open_first_order(self) -> OrderDetailPage:
        self.click(self.FIRST_ORDER)
        self.page.wait_for_load_state("networkidle")
        return OrderDetailPage(self.page)

    def order_count(self) -> int:
        return self.page.locator(self.ORDER_ROW).count()
