from appium.webdriver.common.appiumby import AppiumBy
from screens.base_screen import BaseScreen


class AndroidVerifiedScreen(BaseScreen):
    VERIFIED_TITLE = (AppiumBy.XPATH, '//android.widget.TextView[@text="Your number has been verified!"]')
    PROCEED_BTN    = (AppiumBy.XPATH, '//android.view.ViewGroup[@content-desc="Proceed"]')

    # ------------------------------------------------------------------ #

    def is_visible(self, timeout: int = 15) -> bool:
        return super().is_visible(self.VERIFIED_TITLE, timeout=timeout)

    def tap_proceed(self):
        self.tap(self.PROCEED_BTN)
