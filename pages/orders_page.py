from pages.base_page import BasePage


class OrdersPage(BasePage):
    HEADING          = ":text('Orders')"
    REF_SEARCH       = "thead input:nth-of-type(1)"
    BRAND_SEARCH     = "thead input:nth-of-type(2)"
    PAYMENT_SELECT   = "thead select, thead [class*='Select']"
    DATE_FILTER      = "thead input[placeholder='DD/MM/YYYY']"
    TABLE_ROWS       = "tbody tr"
    ORDER_LINKS      = "tbody tr td:first-child a"
    DATE_FROM        = "input[placeholder*='2026']:first-of-type"

    def is_loaded(self) -> bool:
        self.wait_for_spinner_gone()
        return self.is_visible(self.HEADING)

    def search_reference(self, ref: str):
        self.page.locator(self.REF_SEARCH).fill(ref)
        self.wait_for_network_idle()

    def search_brand(self, brand: str):
        self.page.locator(self.BRAND_SEARCH).fill(brand)
        self.wait_for_network_idle()

    def filter_payment_mode(self, mode: str):
        sel = self.page.locator("thead").get_by_role("combobox")
        sel.select_option(label=mode)
        self.wait_for_network_idle()

    def click_sort(self, col_text: str):
        self.page.locator(f"th:has-text('{col_text}')").click()
        self.wait_for_spinner_gone()

    def get_row_count(self) -> int:
        return self.page.locator(self.TABLE_ROWS).count()

    def get_first_ref_code(self) -> str:
        return self.page.locator(self.ORDER_LINKS).first.inner_text().strip()

    def click_first_order(self):
        self.page.locator(self.ORDER_LINKS).first.click()
        self.wait_for_network_idle()
