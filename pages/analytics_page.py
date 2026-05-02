from pages.base_page import BasePage


class AnalyticsPage(BasePage):
    HEADING           = ":text('Analytics')"
    TAB_OPERATIONS    = ":text('Operations')"
    TAB_BUSINESS      = ":text('Business')"
    TAB_BRANDS        = ":text('Brands')"

    BRAND_FILTER      = "[class*='Select']:has-text('Select Brand')"
    DARKSTORE_FILTER  = "[class*='Select']:has-text('Select Darkstore')"
    PRESET_FILTER     = "[class*='Select']:has-text('Select Preset')"
    SAVE_PRESET_BTN   = "button:has-text('Save Preset')"
    CLEAR_ALL_BTN     = "button:has-text('Clear All')"
    DATE_FROM         = "input[placeholder*='2026']:first-of-type, input[type='date']:first-of-type"

    CHART_CONTAINER   = "[class*='chart'], canvas, svg[class*='recharts']"
    ORDERS_PER_DAY    = ":text('Orders Per Day')"

    TABS = {
        "operations": ":text('Operations')",
        "business":   ":text('Business')",
        "brands":     ":text('Brands')",
    }

    def is_loaded(self) -> bool:
        try:
            self.expect_visible(self.HEADING, timeout=15000)
            return True
        except Exception:
            return False

    def click_tab(self, tab: str):
        self.page.locator(self.TABS[tab]).click()
        self.wait_for_spinner_gone()

    def is_operations_tab_active(self) -> bool:
        el = self.page.locator(self.TAB_OPERATIONS)
        cls = el.get_attribute("class") or ""
        return "active" in cls or "primary" in cls or "purple" in cls

    def click_clear_all(self):
        self.page.locator(self.CLEAR_ALL_BTN).click()
        self.wait_for_spinner_gone()

    def charts_visible(self) -> bool:
        return self.page.locator(self.ORDERS_PER_DAY).count() > 0
