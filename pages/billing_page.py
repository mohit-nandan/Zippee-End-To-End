from pages.base_page import BasePage


class BillingPage(BasePage):
    HEADING             = ":text('Billing & Invoices')"
    TAB_DEDUCTIONS      = ":text('Deductions')"
    TAB_INVOICES        = ":text('Invoices')"
    SUBTAB_DAILY        = "button:has-text('Daily Summary'), :text('Daily Summary')"
    SUBTAB_DEDUCTION    = ":text('Deduction View')"

    STAT_TOTAL_USAGE    = ":text('Total Usage')"
    STAT_GENERAL_USAGE  = ":text('General Usage')"
    STAT_MISC_USAGE     = ":text('Miscellaneous Usage')"
    STAT_NUM_DEDUCTIONS = ":text('No. of Deductions')"

    GEN_INVOICE_BTN     = "button:has-text('Generate Invoice')"
    SEND_INVOICES_BTN   = "button:has-text('Send Invoices')"
    MG_ADJUSTMENT_BTN   = "button:has-text('MG Adjustment')"

    BRAND_FILTER        = "[class*='Select']:has-text('Brand'), select[name='brand']"
    DARKSTORE_FILTER    = "[class*='Select']:has-text('Darkstore'), select[name='darkstore']"
    DATE_SEARCH         = "thead input[placeholder='DD/MM/YYYY']"
    TABLE_ROWS          = "tbody tr"

    def is_loaded(self) -> bool:
        self.wait_for_spinner_gone()
        return self.is_visible(self.HEADING)

    def click_tab(self, tab: str):
        tabs = {"deductions": self.TAB_DEDUCTIONS, "invoices": self.TAB_INVOICES}
        self.page.locator(tabs[tab]).click()
        self.wait_for_spinner_gone()

    def click_subtab(self, subtab: str):
        subs = {"daily": self.SUBTAB_DAILY, "deduction_view": self.SUBTAB_DEDUCTION}
        self.page.locator(subs[subtab]).first.click()
        self.wait_for_spinner_gone()

    def stats_visible(self) -> bool:
        return (
            self.is_visible(self.STAT_TOTAL_USAGE) and
            self.is_visible(self.STAT_GENERAL_USAGE)
        )

    def click_generate_invoice(self):
        self.page.locator(self.GEN_INVOICE_BTN).click()

    def get_row_count(self) -> int:
        return self.page.locator(self.TABLE_ROWS).count()
