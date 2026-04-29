from appium.webdriver.common.appiumby import AppiumBy
from screens.base_screen import BaseScreen


class OtpScreen(BaseScreen):
    _PHONE_INPUT    = (AppiumBy.XPATH, '//android.widget.EditText[@index="0"]')
    _SEND_OTP_BTN   = (AppiumBy.XPATH, '//android.widget.Button[@text="Send OTP" or @content-desc="Send OTP"]')
    _OTP_INPUT      = (AppiumBy.XPATH, '//android.widget.EditText[@index="1"]')
    _VERIFY_BTN     = (AppiumBy.XPATH, '//android.widget.Button[@text="Verify" or @content-desc="Verify"]')
    _ERROR_MSG      = (AppiumBy.XPATH, '//*[contains(@text,"Invalid") or contains(@text,"incorrect")]')

    def enter_phone(self, phone: str):
        self.fill(self._PHONE_INPUT, phone)

    def tap_send_otp(self):
        self.tap(self._SEND_OTP_BTN)

    def enter_otp(self, otp: str):
        self.fill(self._OTP_INPUT, otp)

    def tap_verify(self):
        self.tap(self._VERIFY_BTN)

    def is_error_visible(self) -> bool:
        return self.is_visible(self._ERROR_MSG)

    def login(self, phone: str, otp: str):
        self.enter_phone(phone)
        self.tap_send_otp()
        self.enter_otp(otp)
        self.tap_verify()
