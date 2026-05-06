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
    NO_DATA_ROW      = "tbody tr td[colspan], tbody :text('No data'), tbody :text('No results'), tbody :text('No records')"
    STAT_CARDS       = "[class*='card'] [class*='skeleton'], [class*='stat-card']"

    # Column search inputs — scoped to type="search" to avoid matching date/select/hidden inputs
    _SEARCH_INPUT = 'thead input[type="search"]'
    COL_SEARCH = {
        "brand_name":     0,
        "wallet_balance": 1,
        "category":       2,
    }

    def is_loaded(self) -> bool:
        try:
            self.expect_visible(self.HEADING, timeout=15000)
            return True
        except Exception:
            return False

    def search_column(self, col: str, value: str):
        locator = self.page.locator(self._SEARCH_INPUT).nth(self.COL_SEARCH[col])
        locator.click(click_count=3)
        if value:
            # press_sequentially fires React's onChange per keystroke (fill() bypasses it)
            locator.press_sequentially(value)
        else:
            locator.press("Control+a")
            locator.press("Backspace")
        self.wait_for_spinner_gone()

    def clear_search(self, col: str):
        self.search_column(col, "")

    def click_sort(self, column_header: str):
        self.page.locator(f"th:has-text('{column_header}')").click()
        self.wait_for_spinner_gone()

    def click_add_brand(self):
        self.page.locator(self.ADD_BRAND_BTN).click()

    def get_row_count(self) -> int:
        return self.page.locator(self.TABLE_ROWS).count()

    def expect_empty_table(self, timeout: int = 8000):
        """Pass if table has 0 data rows OR shows a 'no data' placeholder row."""
        from playwright.sync_api import expect
        try:
            expect(self.page.locator(self.NO_DATA_ROW)).to_be_visible(timeout=timeout)
        except Exception:
            # Fallback: table literally has 0 rows
            self.expect_row_count(0, timeout=timeout)

    def get_first_brand_name(self) -> str:
        return self.page.locator(f"{self.TABLE_ROWS}:first-child td:first-child").inner_text().strip()

    def click_first_brand_row(self, expected_name: str):
        """
        Mirrors Cypress:
            cy.get("tbody tr").first().find("td").first()
              .should("contain.text", searchName)
              .find('a').click();

        1. Asserts the first row's first cell contains `expected_name`.
        2. Clicks the <a> link inside that cell.
        """
        first_cell = self.page.locator("tbody tr").first.locator("td").first
        # Assert the cell contains the expected brand name (auto-retrying)
        from playwright.sync_api import expect
        expect(first_cell).to_contain_text(expected_name, timeout=10000)
        # Click the anchor link inside that cell
        first_cell.locator("a").click()
        self.page.wait_for_load_state("domcontentloaded")

    def set_status_filter(self, value: str):
        self.page.locator("select, [class*='Select']").last.select_option(value)
        self.wait_for_network_idle()
