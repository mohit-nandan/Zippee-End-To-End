from pages.base_page import BasePage


class HomePage(BasePage):
    STAT_CARDS      = "[class*='stat'], [class*='card']"
    NEW_ORDERS_CARD = ":text('New Orders Received Today')"
    PREPAID_CARD    = ":text('of Prepaid Orders')"
    DELIVERED_CARD  = ":text('Delivered Orders Today')"
    BRAND_DROPDOWN  = "text=Select Brand"
    COVERAGE_MAP    = ":text('Zippee Coverage')"

    def is_loaded(self) -> bool:
        return self.is_visible(self.NEW_ORDERS_CARD)

    def get_new_orders_count(self) -> str:
        card = self.page.locator(self.NEW_ORDERS_CARD).locator("..").locator("..")
        return card.inner_text().split("\n")[0].strip()

    def is_coverage_section_visible(self) -> bool:
        return self.is_visible(self.COVERAGE_MAP)

    def select_brand(self, brand_name: str):
        self.page.locator(self.BRAND_DROPDOWN).click()
        self.page.get_by_role("option", name=brand_name).click()
