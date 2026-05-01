from pages.base_page import BasePage


class ShipmentsPage(BasePage):
    HEADING             = ":text('Shipments')"
    STAT_TOTAL          = ":text('Total Shipments')"
    STAT_OPEN           = ":text('Open Shipments')"
    STAT_FAILED         = ":text('Failed Shipments')"
    STAT_PROCESSED      = ":text('Processed Shipments')"
    AWB_SEARCH          = "th:has-text('Zippee AWB') ~ tr input, thead input:nth-of-type(1)"
    DARKSTORE_SEARCH    = "thead input:nth-of-type(2)"
    STATUS_SELECT       = "thead select, thead [class*='Select']"
    DATE_INPUT          = "thead input[placeholder='DD/MM/YYYY']"
    ORDER_TYPE_DROPDOWN = "[class*='Select']:has-text('Order Type'), select"
    TABLE_ROWS          = "tbody tr, table tr[class*='row']"
    AWB_LINKS           = "tbody tr td:first-child a, tbody a[href*='shipment']"
    DOWNLOAD_BTN        = "button:has(svg)[aria-label*='download'], button:has-text('download')"
    REFIRE_BTN          = "button:has-text('Refire')"
    BULK_ACTION_BTN     = "button:has-text('Bulk Action Logs')"
    DATE_FROM           = "input[placeholder='01/05/2026']:first-of-type, input[type='date']:first-of-type"

    # Column search selectors (positional, 0-indexed in thead second row)
    COL_SEARCH = {
        "awb":       "thead tr:last-child td:nth-child(1) input",
        "status":    "thead tr:last-child td:nth-child(2) select",
        "darkstore": "thead tr:last-child td:nth-child(3) input",
        "date":      "thead tr:last-child td:nth-child(4) input",
        "order_type":"thead tr:last-child td:nth-child(5)",
    }

    def is_loaded(self) -> bool:
        return self.is_visible(self.STAT_TOTAL)

    def get_total_count(self) -> int:
        try:
            text = self.page.locator(self.STAT_TOTAL).locator("..").inner_text()
            return int(text.split()[0])
        except Exception:
            return 0

    def search_awb(self, awb: str):
        inp = self.page.locator("thead input").first
        inp.fill(awb)
        self.wait_for_network_idle()

    def filter_status(self, status: str):
        sel = self.page.locator("thead").get_by_role("combobox").first
        sel.select_option(label=status)
        self.wait_for_network_idle()

    def search_darkstore(self, value: str):
        inp = self.page.locator("thead input").nth(1)
        inp.fill(value)
        self.wait_for_network_idle()

    def click_sort(self, col_text: str):
        self.page.locator(f"th:has-text('{col_text}')").click()
        self.wait_for_spinner_gone()

    def get_row_count(self) -> int:
        return self.page.locator(self.TABLE_ROWS).count()

    def get_first_awb(self) -> str:
        return self.page.locator(self.AWB_LINKS).first.inner_text().strip()

    def click_first_shipment(self):
        self.page.locator(self.AWB_LINKS).first.click()
        self.wait_for_network_idle()

    def click_refire(self):
        self.page.locator(self.REFIRE_BTN).click()
