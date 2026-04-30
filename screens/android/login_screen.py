from appium.webdriver.common.appiumby import AppiumBy
from screens.base_screen import BaseScreen


class AndroidLoginScreen(BaseScreen):
    # Splash / landing
    LOGIN_BTN  = (AppiumBy.XPATH, '//android.view.ViewGroup[@content-desc="Log In"]')
    SIGNUP_BTN = (AppiumBy.XPATH, '//android.view.ViewGroup[@content-desc="Sign Up"]')

    # Phone entry screen
    PHONE_INPUT  = (AppiumBy.XPATH, '//android.widget.EditText')
    PROCEED_BTN  = (AppiumBy.XPATH, '//android.view.ViewGroup[@content-desc="Proceed"]')

    # OTP screen
    OTP_DIGIT    = (AppiumBy.XPATH, '//android.view.ViewGroup[@content-desc="OTP digit"]')
    SUBMIT_BTN   = (AppiumBy.XPATH, '//android.view.ViewGroup[@content-desc="Submit"]')
    RESEND_BTN   = (AppiumBy.XPATH, '//android.view.ViewGroup[@content-desc="Resend code"]')
    OTP_TITLE    = (AppiumBy.XPATH, '//android.widget.TextView[@text="Verify OTP"]')
    ERROR_MSG    = (AppiumBy.XPATH, '//*[contains(@text,"Invalid") or contains(@text,"incorrect") or contains(@text,"Wrong")]')

    # ------------------------------------------------------------------ #

    def tap_login(self):
        self.tap(self.LOGIN_BTN)

    def tap_signup(self):
        self.tap(self.SIGNUP_BTN)

    def enter_phone(self, phone: str):
        self.fill(self.PHONE_INPUT, phone)

    def tap_proceed(self):
        self.tap(self.PROCEED_BTN)

    def wait_for_otp_screen(self, timeout: int = 15) -> bool:
        return self.is_visible(self.OTP_TITLE, timeout=timeout)

    def enter_otp(self, otp: str):
        """Focus the first OTP box then type each digit via adb keyevents."""
        first_box = (AppiumBy.XPATH, '(//android.view.ViewGroup[@content-desc="OTP digit"])[1]')
        self.tap(first_box)
        self.tap(first_box)
        self.type_via_keyevent(otp)

    def tap_submit(self):
        self.tap(self.SUBMIT_BTN)

    def is_error_visible(self, timeout: int = 5) -> bool:
        return self.is_visible(self.ERROR_MSG, timeout=timeout)

    def login(self, phone: str, otp: str):
        """Full login flow: phone → proceed → OTP → submit."""
        self.tap_login()
        self.enter_phone(phone)
        self.tap_proceed()
        self.wait_for_otp_screen()
        self.enter_otp(otp)
        self.tap_submit()
