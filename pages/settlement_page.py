from pages.base_page import BasePage


class SettlementPage(BasePage):
    TAB_RIDER       = ":text('Rider')"
    TAB_DARKSTORE   = ":text('Dark Store')"
    TAB_COMPANY     = ":text('Company')"
    TAB_BRAND       = ":text('Brand')"

    DARKSTORE_FILTER = "select, [class*='Select']:has-text('All Darkstores')"
    TOGGLE_RIDER     = "button:has-text('Rider'):not([role='tab'])"
    TOGGLE_SETTLEMENT= "button:has-text('Settlement'):not([role='tab'])"

    TABLE_ROWS       = "tbody tr"

    TABS = {
        "rider":      ":text('Rider')",
        "dark_store": ":text('Dark Store')",
        "company":    ":text('Company')",
        "brand":      ":text('Brand')",
    }

    def is_loaded(self) -> bool:
        try:
            self.expect_visible(self.TAB_RIDER, timeout=15000)
            return True
        except Exception:
            return False

    def click_tab(self, tab: str):
        self.page.locator(self.TABS[tab]).first.click()
        self.wait_for_spinner_gone()

    def select_darkstore(self, name: str):
        self.page.locator(self.DARKSTORE_FILTER).select_option(label=name)
        self.wait_for_network_idle()

    def toggle_to_rider_view(self):
        self.page.locator(self.TOGGLE_RIDER).click()
        self.wait_for_spinner_gone()

    def toggle_to_settlement_view(self):
        self.page.locator(self.TOGGLE_SETTLEMENT).click()
        self.wait_for_spinner_gone()

    def get_row_count(self) -> int:
        return self.page.locator(self.TABLE_ROWS).count()
