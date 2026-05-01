from pages.base_page import BasePage


class BrandsPage(BasePage):
    HEADING          = ":text('All Brands')"
    ADD_BRAND_BTN    = "button:has-text('Add Brand')"
    DOWNLOAD_BTN     = "button[title*='download'], button[aria-label*='download'], button:has(svg):last-of-type"
    NAME_SEARCH      = "th:has-text('Brand Name') ~ * input, table thead tr td:nth-child(1) input"
    WALLET_SEARCH    = "table thead tr:nth-child(2) td:nth-child(2) input"
    CATEGORY_SEARCH  = "table thead tr:nth-child(2) td:nth-child(3) input"
    STATUS_SELECT    = "select, [class*='select']"
    SORT_BRAND_NAME  = "th:has-text('Brand Name') button, th:has-text('Brand Name')"
    TABLE_ROWS       = "tbody tr"
    STAT_CARDS       = "[class*='card'] [class*='skeleton'], [class*='stat-card']"

    # Column search inputs (inline in thead)
    COL_SEARCH = {
        "brand_name":     "thead input:nth-of-type(1)",
        "wallet_balance": "thead input:nth-of-type(2)",
        "category":       "thead input:nth-of-type(3)",
    }

    def is_loaded(self) -> bool:
        return self.is_visible(self.HEADING)

    def search_column(self, col: str, value: str):
        self.page.locator(self.COL_SEARCH[col]).fill(value)
        self.wait_for_network_idle()

    def clear_search(self, col: str):
        self.page.locator(self.COL_SEARCH[col]).clear()
        self.wait_for_network_idle()

    def click_sort(self, column_header: str):
        self.page.locator(f"th:has-text('{column_header}')").click()
        self.wait_for_spinner_gone()

    def click_add_brand(self):
        self.page.locator(self.ADD_BRAND_BTN).click()

    def get_row_count(self) -> int:
        return self.page.locator(self.TABLE_ROWS).count()

    def get_first_brand_name(self) -> str:
        return self.page.locator(f"{self.TABLE_ROWS}:first-child td:first-child").inner_text().strip()

    def set_status_filter(self, value: str):
        self.page.locator("select, [class*='Select']").last.select_option(value)
        self.wait_for_network_idle()
