from appium.webdriver.common.appiumby import AppiumBy
from screens.base_screen import BaseScreen


class AndroidSignupScreen(BaseScreen):
    # Registration form (screen 1)
    FIRST_NAME_INPUT = (AppiumBy.XPATH, '(//android.widget.EditText)[1]')
    LAST_NAME_INPUT  = (AppiumBy.XPATH, '(//android.widget.EditText)[2]')
    PHONE_INPUT      = (AppiumBy.XPATH, '(//android.widget.EditText)[3]')
    FORM_SUBMIT_BTN  = (AppiumBy.XPATH, '//android.view.ViewGroup[@content-desc="Submit"]')

    # OTP screen (identical structure to login OTP screen)
    OTP_TITLE        = (AppiumBy.XPATH, '//android.widget.TextView[@text="Verify OTP"]')
    OTP_FIRST_BOX    = (AppiumBy.XPATH, '(//android.view.ViewGroup[@content-desc="OTP digit"])[1]')
    OTP_SUBMIT_BTN   = (AppiumBy.XPATH, '//android.view.ViewGroup[@content-desc="Submit"]')
    RESEND_BTN       = (AppiumBy.XPATH, '//android.view.ViewGroup[@content-desc="Resend code"]')
    ERROR_MSG        = (AppiumBy.XPATH, '//*[contains(@text,"Invalid") or contains(@text,"incorrect") or contains(@text,"Wrong") or contains(@text,"already")]')

    # ------------------------------------------------------------------ #

    def enter_first_name(self, name: str):
        el = self.driver.find_element(*self.FIRST_NAME_INPUT)
        el.clear()
        el.send_keys(name)

    def enter_last_name(self, name: str):
        el = self.driver.find_element(*self.LAST_NAME_INPUT)
        el.clear()
        el.send_keys(name)

    def enter_phone(self, phone: str):
        self.fill(self.PHONE_INPUT, phone)

    def tap_submit(self):
        self.tap(self.FORM_SUBMIT_BTN)

    def wait_for_otp_screen(self, timeout: int = 15) -> bool:
        return self.is_visible(self.OTP_TITLE, timeout=timeout)

    def enter_otp(self, otp: str):
        """Focus the first OTP box then type each digit via adb keyevents."""
        self.tap(self.OTP_FIRST_BOX)
        self.tap(self.OTP_FIRST_BOX)
        self.type_via_keyevent(otp)

    def tap_submit_otp(self):
        self.tap(self.OTP_SUBMIT_BTN)

    def is_error_visible(self, timeout: int = 5) -> bool:
        return self.is_visible(self.ERROR_MSG, timeout=timeout)

    def signup(self, first_name: str, last_name: str, phone: str, otp: str):
        """Full registration flow: form → OTP → submit."""
        self.enter_first_name(first_name)
        self.enter_last_name(last_name)
        self.enter_phone(phone)
        self.tap_submit()
        self.wait_for_otp_screen()
        self.enter_otp(otp)
        self.tap_submit_otp()
