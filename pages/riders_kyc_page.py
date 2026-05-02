from pages.base_page import BasePage


class RidersKycPage(BasePage):
    HEADING           = ":text('KYC Verification')"
    DARKSTORE_FILTER  = "select, [class*='Select']:has-text('All Darkstores')"
    RIDER_SEARCH      = "input[placeholder='Search Rider Name']"
    CITY_SEARCH       = "input[placeholder='Search City']"
    DARKSTORE_SEARCH  = "input[placeholder='Search Darkstore']"
    PAN_SEARCH        = "input[placeholder='Search PA'], input[placeholder*='PAN']"
    DOWNLOAD_BTN      = "button[title*='download'], a[download], button:has(svg):last-of-type"
    CLEAR_BTN         = ":text('Clear Filters')"
    TABLE_ROWS        = "tbody tr"
    STATUS_APPROVED   = ":text('Approved')"
    STATUS_PENDING    = ":text('Pending')"

    def is_loaded(self) -> bool:
        try:
            self.expect_visible(self.HEADING, timeout=15000)
            return True
        except Exception:
            return False

    def search_rider(self, name: str):
        self.page.locator(self.RIDER_SEARCH).fill(name)
        self.wait_for_network_idle()

    def search_city(self, city: str):
        self.page.locator(self.CITY_SEARCH).fill(city)
        self.wait_for_network_idle()

    def search_darkstore(self, ds: str):
        self.page.locator(self.DARKSTORE_SEARCH).fill(ds)
        self.wait_for_network_idle()

    def select_darkstore_filter(self, name: str):
        self.page.locator(self.DARKSTORE_FILTER).select_option(label=name)
        self.wait_for_network_idle()

    def clear_filters(self):
        self.page.locator(self.CLEAR_BTN).click()
        self.wait_for_network_idle()

    def click_sort(self, col: str):
        self.page.locator(f"th:has-text('{col}')").click()
        self.wait_for_spinner_gone()

    def get_row_count(self) -> int:
        return self.page.locator(self.TABLE_ROWS).count()
