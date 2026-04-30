from appium.webdriver.common.appiumby import AppiumBy
from screens.base_screen import BaseScreen


class AndroidHomeScreen(BaseScreen):
    # Bottom navigation tabs
    TAB_HOME        = (AppiumBy.XPATH, '//android.view.View[@content-desc="Home"]')
    TAB_DELIVERY    = (AppiumBy.XPATH, '//android.view.View[@content-desc="Delivery"]')
    TAB_ATTENDANCE  = (AppiumBy.XPATH, '//android.view.View[@content-desc="Attendance"]')
    TAB_SETTLEMENTS = (AppiumBy.XPATH, '//android.view.View[@content-desc="Settlements"]')

    # Top bar
    HAMBURGER_BTN   = (AppiumBy.XPATH, '(//android.view.ViewGroup[.//android.widget.ImageView])[1]')
    NOTIFICATIONS   = (AppiumBy.XPATH, '//android.view.ViewGroup[@content-desc="Notifications"]')

    # Home content — used as "home is loaded" sentinel
    _HOME_CONTAINER = TAB_HOME

    # ------------------------------------------------------------------ #

    def is_loaded(self, timeout: int = 15) -> bool:
        return self.is_visible(self.TAB_HOME, timeout=timeout)

    def open_drawer(self):
        self.tap(self.HAMBURGER_BTN)

    def go_to_delivery(self):
        self.tap(self.TAB_DELIVERY)

    def go_to_attendance(self):
        self.tap(self.TAB_ATTENDANCE)

    def go_to_settlements(self):
        self.tap(self.TAB_SETTLEMENTS)

    def go_to_home(self):
        self.tap(self.TAB_HOME)
