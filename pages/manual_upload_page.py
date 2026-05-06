from pages.base_page import BasePage


class ManualUploadPage(BasePage):
    HEADING         = ":text('Manually Added Orders')"
    UPLOAD_BTN      = "button:has-text('Upload')"
    ADD_NEW_BTN     = "button:has-text('Add New'), button:has-text('+ Add New')"
    DOWNLOAD_BTN    = "button[aria-label*='download'], a[download]"
    CLEAR_BTN       = ":text('Clear Filters')"

    ORDER_ID_SEARCH = "input[placeholder='Search Order ID']"
    RIDER_SEARCH    = "input[placeholder='Search Rider Username']"
    DELIVERY_DATE   = "input[placeholder='DD/MM/YYYY']:nth-of-type(1)"
    CREATED_DATE    = "input[placeholder='DD/MM/YYYY']:nth-of-type(2)"

    TABLE_ROWS      = "tbody tr"
    SORT_ORDER_ID   = "th:has-text('Order ID')"
    SORT_RIDER      = "th:has-text('Rider Username')"

    def is_loaded(self) -> bool:
        try:
            self.expect_visible(self.HEADING, timeout=15000)
            return True
        except Exception:
            return False

    def search_order_id(self, order_id: str):
        self.page.locator(self.ORDER_ID_SEARCH).fill(order_id)
        self.wait_for_network_idle()

    def search_rider(self, rider: str):
        self.page.locator(self.RIDER_SEARCH).fill(rider)
        self.wait_for_network_idle()

    def click_sort(self, col: str):
        self.page.locator(f"th:has-text('{col}')").click()
        self.wait_for_spinner_gone()

    def click_add_new(self):
        self.page.locator(self.ADD_NEW_BTN).click()

    def click_upload(self):
        self.page.locator(self.UPLOAD_BTN).click()

    def get_row_count(self) -> int:
        return self.page.locator(self.TABLE_ROWS).count()
