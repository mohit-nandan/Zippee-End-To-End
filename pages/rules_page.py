from pages.base_page import BasePage


class RulesPage(BasePage):
    HEADING       = ":text('Rules Management')"
    ADD_BTN       = "button:has-text('Add')"
    NAME_SEARCH   = "thead input:nth-of-type(1)"
    DESC_SEARCH   = "thead input:nth-of-type(2)"
    STATUS_SELECT = "thead select, thead [class*='Select']"
    DS_SEARCH     = "thead input:nth-of-type(3)"
    TABLE_ROWS    = "tbody tr"
    RULE_LINKS    = "tbody tr td:first-child a"
    SORT_NAME     = "th:has-text('Name')"

    def is_loaded(self) -> bool:
        self.wait_for_spinner_gone()
        return self.is_visible(self.HEADING)

    def search_name(self, value: str):
        self.page.locator(self.NAME_SEARCH).fill(value)
        self.wait_for_network_idle()

    def search_description(self, value: str):
        self.page.locator(self.DESC_SEARCH).fill(value)
        self.wait_for_network_idle()

    def filter_status(self, status: str):
        self.page.locator(self.STATUS_SELECT).select_option(label=status)
        self.wait_for_network_idle()

    def click_sort_name(self):
        self.page.locator(self.SORT_NAME).click()
        self.wait_for_spinner_gone()

    def get_row_count(self) -> int:
        return self.page.locator(self.TABLE_ROWS).count()

    def click_rule(self, name: str):
        self.page.locator(f"a:has-text('{name}')").click()
        self.wait_for_network_idle()
