from appium.webdriver.common.appiumby import AppiumBy
from screens.base_screen import BaseScreen


class AndroidDeliveryScreen(BaseScreen):
    OTP_INPUT       = (AppiumBy.ID, "com.zippee.rider:id/delivery_otp_input")
    CONFIRM_BTN     = (AppiumBy.ID, "com.zippee.rider:id/confirm_delivery_btn")
    STATUS_TEXT     = (AppiumBy.ID, "com.zippee.rider:id/delivery_status")
    ATTEMPT_BTN     = (AppiumBy.ID, "com.zippee.rider:id/delivery_attempted_btn")

    def confirm_delivery(self, otp: str):
        self.fill(self.OTP_INPUT, otp)
        self.tap(self.CONFIRM_BTN)

    def get_status(self) -> str:
        return self.get_text(self.STATUS_TEXT)

    def mark_delivery_attempted(self, reason: str):
        self.tap(self.ATTEMPT_BTN)
        self.driver.find_element(
            AppiumBy.ANDROID_UIAUTOMATOR,
            f'new UiSelector().text("{reason}")'
        ).click()
