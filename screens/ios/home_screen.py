from appium.webdriver.common.appiumby import AppiumBy
from screens.base_screen import BaseScreen


class IOSHomeScreen(BaseScreen):
    ORDER_LIST_TAB   = (AppiumBy.ACCESSIBILITY_ID, "tab_orders")
    FIRST_ORDER_ITEM = (AppiumBy.XPATH, "//XCUIElementTypeCell[1]")
    ATTENDANCE_BTN   = (AppiumBy.ACCESSIBILITY_ID, "mark_attendance_btn")
    WELCOME_TEXT     = (AppiumBy.ACCESSIBILITY_ID, "welcome_text")

    def is_loaded(self) -> bool:
        return self.is_visible(self.WELCOME_TEXT)

    def go_to_orders(self):
        self.tap(self.ORDER_LIST_TAB)

    def tap_first_order(self):
        self.tap(self.FIRST_ORDER_ITEM)

    def mark_attendance(self):
        self.tap(self.ATTENDANCE_BTN)
