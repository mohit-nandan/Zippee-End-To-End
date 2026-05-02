from pages.base_page import BasePage


class DeliveriesPage(BasePage):
    HEADING        = ":text('Deliveries')"
    TAB_SHIPMENTS  = "text=Shipments"
    TAB_TRIPS      = "text=Trips"

    # Shipment sub-tabs
    TAB_ASSIGN_NOW   = "button:has-text('Assign Now'), :text('Assign Now')"
    TAB_ASSIGN_LATER = ":text('Assign Later')"
    TAB_ASSIGNED     = ":text('Assigned')"
    TAB_COMPLETED    = ":text('Completed')"
    TAB_RETURN       = ":text('Return')"
    TAB_ALL          = ":text('All Shipments')"

    CREATE_TRIP_BTN  = "button:has-text('+ Create Trip'), button:has-text('Create Trip')"
    DOWNLOAD_BTN     = "button:has(svg)[aria-label*='download']"

    AWB_SEARCH       = "thead input:nth-of-type(1)"
    ORDER_SEARCH     = "thead input:nth-of-type(2)"
    BRAND_SEARCH     = "thead input:nth-of-type(3)"
    STATUS_SELECT    = "thead [class*='Select'], thead select"
    TABLE_ROWS       = "tbody tr"

    def is_loaded(self) -> bool:
        try:
            self.expect_visible(self.TAB_SHIPMENTS, timeout=15000)
            return True
        except Exception:
            return False

    def click_tab(self, tab_name: str):
        tabs = {
            "shipments":     self.TAB_SHIPMENTS,
            "trips":         self.TAB_TRIPS,
            "assign_now":    self.TAB_ASSIGN_NOW,
            "assign_later":  self.TAB_ASSIGN_LATER,
            "assigned":      self.TAB_ASSIGNED,
            "completed":     self.TAB_COMPLETED,
            "return":        self.TAB_RETURN,
            "all_shipments": self.TAB_ALL,
        }
        self.page.locator(tabs[tab_name]).first.click()
        self.wait_for_spinner_gone()

    def search_awb(self, awb: str):
        self.page.locator(self.AWB_SEARCH).fill(awb)
        self.wait_for_network_idle()

    def search_order_number(self, value: str):
        self.page.locator(self.ORDER_SEARCH).fill(value)
        self.wait_for_network_idle()

    def search_brand(self, brand: str):
        self.page.locator(self.BRAND_SEARCH).fill(brand)
        self.wait_for_network_idle()

    def filter_status(self, status: str):
        self.page.locator(self.STATUS_SELECT).select_option(label=status)
        self.wait_for_network_idle()

    def get_row_count(self) -> int:
        return self.page.locator(self.TABLE_ROWS).count()

    def click_create_trip(self):
        self.page.locator(self.CREATE_TRIP_BTN).click()
